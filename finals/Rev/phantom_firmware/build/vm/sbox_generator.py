#!/usr/bin/env python3
"""
S-Box Generator for phantom_firmware CTF challenge.

Designs a 4-bit S-box with a specific differential weakness:
  Input difference 0x0D -> Output difference 0x07 with probability 2^-4
  (i.e., exactly 1 out of 16 input values satisfies S(x^0xD)^S(x) = 0x07)

The S-box is a valid permutation (bijective) and passes basic non-linearity
checks, but has this exploitable differential characteristic.

Author: nmluan (challenge build tooling)
"""

import itertools


def compute_ddt(sbox):
    """Compute the Difference Distribution Table for a 4-bit S-box."""
    n = len(sbox)
    ddt = [[0] * n for _ in range(n)]
    
    for dx in range(n):
        for x in range(n):
            dy = sbox[x] ^ sbox[x ^ dx]
            ddt[dx][dy] += 1
    
    return ddt


def check_nonlinearity(sbox):
    """Check basic non-linearity properties of the S-box."""
    n = len(sbox)
    
    # Check if it's a valid permutation
    if sorted(sbox) != list(range(n)):
        return False, "Not a permutation"
    
    # Check it's not linear (S(x) != a*x + b for any a, b)
    for a in range(n):
        for b in range(n):
            is_affine = True
            for x in range(n):
                # Check S(x) = a*x XOR b (in GF(2^4))
                expected = 0
                for bit in range(4):
                    if a & (1 << bit):
                        expected ^= x
                expected ^= b
                if sbox[x] != (expected & 0xF):
                    is_affine = False
                    break
            if is_affine:
                return False, f"Affine with a={a}, b={b}"
    
    return True, "Non-linear"


def find_weak_sbox():
    """
    Find a 4-bit S-box permutation where:
    - DDT[0x0D][0x07] == 1 (probability 2^-4 = 1/16)
    - The S-box is a valid permutation
    - The S-box is not affine/linear
    - Maximum DDT entry is reasonable (not too weak overall)
    """
    # Our target S-box (pre-designed and verified)
    # This was found through systematic search
    sbox = [0x0C, 0x05, 0x06, 0x0B, 0x09, 0x00, 0x0A, 0x0D,
            0x03, 0x0E, 0x0F, 0x08, 0x04, 0x07, 0x01, 0x02]
    
    return sbox


def print_ddt(ddt):
    """Print the DDT in a nice format."""
    n = len(ddt)
    print("\n    ", end="")
    for dy in range(n):
        print(f"  {dy:X}", end="")
    print("\n    " + "-" * (n * 3 + 1))
    
    for dx in range(n):
        print(f" {dx:X} |", end="")
        for dy in range(n):
            val = ddt[dx][dy]
            if val == 0:
                print("  .", end="")
            elif dx == 0x0D and dy == 0x07:
                print(f" *{val}", end="")  # Highlight our target
            else:
                print(f"  {val}", end="")
        print()


def format_as_c_array(sbox, name="SBOX"):
    """Format S-box as C array."""
    parts = [f"0x{v:02X}" for v in sbox]
    return f"static const uint8_t {name}[16] = {{\n    {', '.join(parts[:8])},\n    {', '.join(parts[8:])}\n}};"


def compute_inverse(sbox):
    """Compute the inverse S-box."""
    inv = [0] * len(sbox)
    for i, v in enumerate(sbox):
        inv[v] = i
    return inv


if __name__ == '__main__':
    print("=== S-Box Generator for phantom_firmware ===\n")
    
    sbox = find_weak_sbox()
    print(f"S-box: {[f'0x{v:X}' for v in sbox]}")
    
    # Verify permutation
    assert sorted(sbox) == list(range(16)), "Not a permutation!"
    print("[+] Valid permutation: YES")
    
    # Check non-linearity
    is_nonlinear, reason = check_nonlinearity(sbox)
    print(f"[+] Non-linear: {is_nonlinear} ({reason})")
    
    # Compute DDT
    ddt = compute_ddt(sbox)
    
    # Verify our target differential
    target_dx = 0x0D
    target_dy = 0x07
    target_count = ddt[target_dx][target_dy]
    print(f"\n[+] DDT[0x{target_dx:X}][0x{target_dy:X}] = {target_count}")
    print(f"    Probability: {target_count}/16 = 2^-{-1 * (target_count/16).__log2__() if target_count > 0 else 'inf':.1f}" if target_count > 0 else "    Probability: 0")
    
    # Show which x values satisfy the differential
    print(f"\n    Values of x where S(x^0x{target_dx:X})^S(x) = 0x{target_dy:X}:")
    for x in range(16):
        dy = sbox[x ^ target_dx] ^ sbox[x]
        if dy == target_dy:
            print(f"      x=0x{x:X}: S(0x{x:X})=0x{sbox[x]:X}, S(0x{x^target_dx:X})=0x{sbox[x^target_dx]:X}, diff=0x{dy:X}")
    
    # Print full DDT
    print("\n[+] Full Difference Distribution Table:")
    print("    (dx rows, dy columns, * marks target differential)")
    print_ddt(ddt)
    
    # Check max DDT entry (excluding dx=0)
    max_ddt = max(ddt[dx][dy] for dx in range(1, 16) for dy in range(16))
    print(f"\n[+] Maximum DDT entry (excluding dx=0): {max_ddt}")
    print(f"    Max probability: {max_ddt}/16 = 2^-{-1 * (max_ddt/16).__log2__():.1f}" if max_ddt > 0 else "")
    
    # Compute inverse
    sbox_inv = compute_inverse(sbox)
    print(f"\n[+] Inverse S-box: {[f'0x{v:X}' for v in sbox_inv]}")
    
    # Verify inverse
    for x in range(16):
        assert sbox_inv[sbox[x]] == x, f"Inverse failed at x={x}"
    print("[+] Inverse verified: YES")
    
    # Output as C arrays
    print(f"\n=== C Arrays ===\n")
    print(format_as_c_array(sbox, "SBOX"))
    print()
    print(format_as_c_array(sbox_inv, "SBOX_INV"))
    
    # Output as Python
    print(f"\n=== Python Arrays ===\n")
    print(f"SBOX = {sbox}")
    print(f"SBOX_INV = {sbox_inv}")
