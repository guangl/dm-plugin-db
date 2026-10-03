#!/usr/bin/env bash
set -euo pipefail
target=${1:?Usage: build_release.sh TARGET}
builder=(cargo build)
build_target=$target
case "$target" in
  *-unknown-linux-gnu) builder=(cargo zigbuild); build_target="$target.2.28" ;;
esac
"${builder[@]}" --release --locked --bin dm-db --target "$build_target"
