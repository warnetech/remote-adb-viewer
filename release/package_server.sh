#!/bin/bash
set -ex
cd "$(dirname ${BASH_SOURCE[0]})"
OUTPUT_DIR="$PWD/output"
. build_common
cd .. # root project dir

mkdir -p "$OUTPUT_DIR"
cp "$WORK_DIR/build-server/server/tainuitech-server" "$OUTPUT_DIR/tainuitech-server-$VERSION"
echo "Generated '$OUTPUT_DIR/tainuitech-server-$VERSION'"
