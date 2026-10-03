"""Validate an independent crate release tag; Python 3.11+."""
import os
from pathlib import Path
import tomllib


def verify():
    with Path("Cargo.toml").open("rb") as source:
        package = tomllib.load(source)["package"]
    tag = os.environ["RELEASE_TAG"]
    if tag != "v" + package["version"]:
        raise SystemExit(f"Tag {tag} must match crate version {package['version']}")
    return tag, package


def package():
    import hashlib
    import shutil
    import tarfile
    import zipfile
    tag, crate = verify()
    with Path("dm-plugin.toml").open("rb") as source:
        manifest = tomllib.load(source)
    if manifest["version"] != crate["version"]:
        raise SystemExit("Plugin manifest and crate versions must match")
    if crate["name"] != "dm-plugin-" + manifest["name"]:
        raise SystemExit("Plugin manifest and crate names must match")
    if manifest["api_version"] != 1:
        raise SystemExit("Unsupported plugin API version")
    target = os.environ["RELEASE_TARGET"]
    labels = {
        "x86_64-unknown-linux-gnu": "x86_64-linux",
        "aarch64-unknown-linux-gnu": "aarch64-linux",
        "armv7-unknown-linux-gnueabihf": "armv7-linux",
        "aarch64-apple-darwin": "aarch64-macos",
        "x86_64-apple-darwin": "x86_64-macos",
        "x86_64-pc-windows-msvc": "x86_64-windows",
        "aarch64-pc-windows-msvc": "aarch64-windows",
    }
    # musl builds reuse the label of the GNU build for the same architecture:
    # they are interchangeable for users and only one asset can carry the name.
    musl_only = {"x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl"}
    if target not in {*labels, *musl_only}:
        raise SystemExit(f"Unsupported release target: {target}")
    windows = target.endswith("windows-msvc")
    binary = "dm-" + manifest["name"] + (".exe" if windows else "")
    source = Path("target") / target / "release" / binary
    dist = Path("dist")
    dist.mkdir(exist_ok=True)
    root = f"dm-{manifest['name']}-{tag}-{target}"
    archive = dist / (root + (".zip" if windows else ".tar.gz"))
    files = [(source, binary)] + [(Path(n), n) for n in
                                 ("dm-plugin.toml", "README.md", "LICENSE", "config.example.toml")]
    for hook in (manifest.get("hooks") or {}).values():
        files.append((Path(hook), hook))
    if windows:
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for path, entry in files:
                output.write(path, f"{root}/{entry}")
    else:
        with tarfile.open(archive, "w:gz") as output:
            for path, entry in files:
                output.add(path, arcname=f"{root}/{entry}")
    assets = [archive]
    if target in labels:
        raw = dist / f"dm-{manifest['name']}-{labels[target]}{'.exe' if windows else ''}"
        shutil.copy2(source, raw)
        assets.append(raw)
    for asset in assets:
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()
        asset.with_name(asset.name + ".sha256").write_text(f"{digest}  {asset.name}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ("verify", "package"):
        raise SystemExit("Usage: release.py verify|package")
    if sys.argv[1] == "verify":
        _, crate = verify()
        with Path("dm-plugin.toml").open("rb") as source:
            manifest = tomllib.load(source)
        if manifest["version"] != crate["version"]:
            raise SystemExit("Plugin manifest and crate versions must match")
        if crate["name"] != "dm-plugin-" + manifest["name"] or manifest["api_version"] != 1:
            raise SystemExit("Invalid plugin name or API version")
    else:
        package()
