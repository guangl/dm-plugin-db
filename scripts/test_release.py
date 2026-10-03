"""Exercise independent release packaging without compiling binaries."""
import hashlib
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
import zipfile
from unittest.mock import patch
import release

ROOT = Path(__file__).resolve().parent.parent


class ReleaseTests(unittest.TestCase):
    def test_all_targets_and_checksums(self):
        for target in ("x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu",
                       "x86_64-unknown-linux-musl", "aarch64-apple-darwin",
                       "x86_64-apple-darwin", "x86_64-pc-windows-msvc"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                previous = Path.cwd()
                try:
                    os.chdir(directory)
                    for name in ("Cargo.toml", "dm-plugin.toml", "README.md", "LICENSE", "config.example.toml"):
                        shutil.copy2(ROOT / name, name)
                    crate = release.tomllib.loads(Path("Cargo.toml").read_text())["package"]
                    name = release.tomllib.loads(Path("dm-plugin.toml").read_text())["name"]
                    binary = "dm-" + name + (".exe" if "windows" in target else "")
                    source = Path("target") / target / "release" / binary
                    source.parent.mkdir(parents=True)
                    source.write_bytes(b"fixture")
                    source.chmod(0o755)
                    tag = "v" + crate["version"]
                    with patch.dict(os.environ, RELEASE_TAG=tag, RELEASE_TARGET=target):
                        release.package()
                    folder = f"dm-{name}-{tag}-{target}"
                    windows = "windows" in target
                    archive = Path("dist") / (folder + (".zip" if windows else ".tar.gz"))
                    if windows:
                        with zipfile.ZipFile(archive) as output:
                            entries = output.namelist()
                    else:
                        with tarfile.open(archive) as output:
                            entries = output.getnames()
                            self.assertEqual(output.getmember(f"{folder}/{binary}").mode, 0o755)
                    self.assertIn(f"{folder}/dm-plugin.toml", entries)
                    self.assertIn(f"{folder}/{binary}", entries)
                    assets = [path for path in Path("dist").iterdir() if not path.name.endswith(".sha256")]
                    self.assertEqual(len(assets), 1 if "musl" in target else 2)
                    for asset in assets:
                        expected = asset.with_name(asset.name + ".sha256").read_text().split()[0]
                        self.assertEqual(expected, hashlib.sha256(asset.read_bytes()).hexdigest())
                    with patch.dict(os.environ, RELEASE_TAG="v9.9.9"):
                        with self.assertRaises(SystemExit):
                            release.verify()
                    Path("dm-plugin.toml").write_text(f'name = "{name}"\nversion = "9.9.9"\napi_version = 1\n')
                    with patch.dict(os.environ, RELEASE_TAG=tag, RELEASE_TARGET=target):
                        with self.assertRaises(SystemExit):
                            release.package()
                finally:
                    os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
