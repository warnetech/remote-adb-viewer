#!/usr/bin/env bash
set -e

BUILDDIR=build-auto

# TainuiTech has no prebuilt server release: the upstream scrcpy server is not
# compatible, so the server is built from source (requires Java and the Android
# SDK, with ANDROID_SDK_ROOT set).
if [[ -z "$ANDROID_SDK_ROOT" && -z "$ANDROID_HOME" ]]; then
    echo "[tainuitech] ANDROID_SDK_ROOT is not set (needed to build the server)" >&2
    exit 1
fi

echo "[tainuitech] Building client and server..."
rm -rf "$BUILDDIR"
meson setup "$BUILDDIR" --buildtype=release --strip -Db_lto=true
cd "$BUILDDIR"
ninja

echo "[tainuitech] Installing (sudo)..."
sudo ninja install
