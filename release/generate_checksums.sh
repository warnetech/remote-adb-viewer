#!/bin/bash
set -ex
cd "$(dirname ${BASH_SOURCE[0]})"
. build_common

cd "$OUTPUT_DIR"
sha256sum "tainuitech-server-$VERSION" \
    "tainuitech-linux-x86_64-$VERSION.tar.gz" \
    "tainuitech-win32-$VERSION.zip" \
    "tainuitech-win64-$VERSION.zip" \
    "tainuitech-winarm64-$VERSION.zip" \
    "tainuitech-macos-aarch64-$VERSION.tar.gz" \
    "tainuitech-macos-x86_64-$VERSION.tar.gz" \
        | tee SHA256SUMS.txt
echo "Release checksums generated in $PWD/SHA256SUMS.txt"
