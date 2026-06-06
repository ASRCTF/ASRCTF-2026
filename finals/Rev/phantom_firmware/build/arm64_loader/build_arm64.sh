#!/bin/bash
# Cross-compile orbital_loader for AArch64 Linux
# Requires: aarch64-linux-gnu-gcc (from gcc-aarch64-linux-gnu package)
#
# Install cross-compilation toolchain:
#   sudo apt install gcc-aarch64-linux-gnu
#   rustup target add aarch64-unknown-linux-gnu

set -e

echo "[*] Building orbital_loader for aarch64-unknown-linux-gnu..."

# Add target if not already present
rustup target add aarch64-unknown-linux-gnu 2>/dev/null || true

# Build release
cargo build --release --target aarch64-unknown-linux-gnu

# Copy to dist
DEST="../../dist/firmware_loader.elf"
mkdir -p "$(dirname "$DEST")"
cp target/aarch64-unknown-linux-gnu/release/orbital_loader "$DEST"

echo "[+] Built: $DEST"
echo "    $(file "$DEST")"
echo "    $(ls -lh "$DEST" | awk '{print $5}')"
