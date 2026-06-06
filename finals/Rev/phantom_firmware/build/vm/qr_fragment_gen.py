#!/usr/bin/env python3
"""
QR Fragment Generator for phantom_firmware CTF challenge.

Generates a 16x16 binary grid that encodes 4 bytes (0xDE, 0xAD, 0xBE, 0xEF).
Each group of 4 rows encodes one byte — the bit pattern is displayed in the 
first 8 columns of the first 2 rows of each group, with a frame border.

Players must visually interpret the grid from the VM's display buffer
to extract the 4-byte cipher key fragment.

Author: nmluan (challenge build tooling)
"""

def generate_qr_fragment(byte_values):
    """
    Generate a 16x16 binary grid encoding up to 4 bytes.
    
    Layout: 
      4 groups of 4 rows, each group encodes one byte
      Rows 0-1 of each group: the 8 bits of the byte (MSB to LSB, left to right)
      Rows 2-3 of each group: border frame (1 at edges, 0 in middle)
      Columns 8-15 are zero (padding)
    """
    grid = [[0] * 16 for _ in range(16)]
    
    for byte_idx, byte_val in enumerate(byte_values[:4]):
        base_row = byte_idx * 4
        
        # Rows 0-1: bit pattern (repeated for redundancy)
        for row_offset in range(2):
            row = base_row + row_offset
            for bit in range(8):
                grid[row][bit] = (byte_val >> (7 - bit)) & 1
        
        # Rows 2-3: frame border
        for row_offset in range(2, 4):
            row = base_row + row_offset
            grid[row][0] = 1  # Left border
            grid[row][7] = 1  # Right border
    
    return grid


def print_grid_ascii(grid):
    """Print the grid as ASCII art."""
    print("    " + "".join(f"{i:2d}" for i in range(16)))
    print("    " + "--" * 16)
    for row_idx, row in enumerate(grid):
        line = f"{row_idx:2d} | "
        for val in row:
            line += "██" if val else "  "
        print(line)


def print_grid_numeric(grid):
    """Print the grid as numeric values."""
    for row_idx, row in enumerate(grid):
        print(f"  Row {row_idx:2d}: [{', '.join(str(v) for v in row)}]")


def decode_qr_fragment(grid):
    """Decode the 4-byte values from the grid (solution verification)."""
    values = []
    for byte_idx in range(4):
        base_row = byte_idx * 4
        byte_val = 0
        for bit in range(8):
            byte_val |= grid[base_row][bit] << (7 - bit)
        values.append(byte_val)
    return bytes(values)


if __name__ == '__main__':
    print("=== QR Fragment Generator ===\n")
    
    target_bytes = bytes([0xDE, 0xAD, 0xBE, 0xEF])
    print(f"Target bytes: {target_bytes.hex()}")
    
    grid = generate_qr_fragment(target_bytes)
    
    print(f"\n--- ASCII Art ---")
    print_grid_ascii(grid)
    
    print(f"\n--- Numeric Grid ---")
    print_grid_numeric(grid)
    
    # Verify decoding
    decoded = decode_qr_fragment(grid)
    assert decoded == target_bytes, f"Decode failed: {decoded.hex()} != {target_bytes.hex()}"
    print(f"\n[+] Decode verified: {decoded.hex()}")
    print("\n=== Done! ===")
