# Cross-compile orbital_loader for AArch64 Linux
# Requires: aarch64-linux-gnu-gcc and Rust aarch64 target
#
# Install on Windows:
#   1. Install MSYS2 and aarch64 cross-toolchain, or use WSL
#   2. rustup target add aarch64-unknown-linux-gnu

Write-Host "[*] Building orbital_loader for aarch64-unknown-linux-gnu..."

# Add target
rustup target add aarch64-unknown-linux-gnu 2>$null

# For native Windows build (x86_64, for testing):
Write-Host "[*] Building native x86_64 for testing..."
cargo build --release

# Copy native build for testing
$TestDest = "..\..\dist\firmware_loader_x64.exe"
New-Item -ItemType Directory -Force -Path (Split-Path $TestDest) | Out-Null
Copy-Item "target\release\orbital_loader.exe" $TestDest -ErrorAction SilentlyContinue

# Try cross-compile (may fail without cross-linker)
Write-Host "[*] Attempting ARM64 cross-compile..."
try {
    cargo build --release --target aarch64-unknown-linux-gnu
    $Dest = "..\..\dist\firmware_loader.elf"
    Copy-Item "target\aarch64-unknown-linux-gnu\release\orbital_loader" $Dest
    Write-Host "[+] ARM64 build: $Dest"
} catch {
    Write-Host "[!] ARM64 cross-compile failed (missing linker?)"
    Write-Host "    Use WSL with build_arm64.sh for ARM64 builds"
    Write-Host "    Native x64 build available for testing: $TestDest"
}
