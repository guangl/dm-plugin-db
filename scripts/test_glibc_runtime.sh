#!/usr/bin/env bash
# Execute the shipped GNU binary against Debian 10's glibc 2.28.
set -euo pipefail
target=${1:?Usage: test_glibc_runtime.sh TARGET}
case "$target" in
  x86_64-unknown-linux-gnu) platform=linux/amd64 ;;
  aarch64-unknown-linux-gnu) platform=linux/arm64 ;;
  armv7-unknown-linux-gnueabihf) platform=linux/arm/v7 ;;
  *) echo "Unsupported GNU target: $target" >&2; exit 1 ;;
esac
# CI uses a native runner where one exists and QEMU for ARMv7, so the platform
# is always stated explicitly.
docker run --rm --platform "$platform" --network none --tmpfs /tmp:rw,exec,nosuid,size=256m \
  -e DM_PLUGIN_API_VERSION=1 -e DM_PLUGIN_CAPABILITIES=config-dirs-v1 \
  -e DM_PLUGIN_HOME=/tmp/home -e DM_PLUGIN_DIR=/artifacts \
  -e DM_PLUGIN_CONFIG_DIR=/tmp/config -e DM_PLUGIN_DATA_DIR=/tmp/data \
  -e DM_PLUGIN_CACHE_DIR=/tmp/cache \
  -v "$PWD/target/$target/release:/artifacts:ro" \
  debian:buster-slim sh -ec '
    ldd --version | head -n 1 | grep -F "2.28"
    /artifacts/dm-db --help
    /artifacts/dm-db list
  '
