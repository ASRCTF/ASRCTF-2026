#!/usr/bin/env python3
"""
Stage 3 Solution: Invisible Unicode Payload Decoder

Discovers and decodes the invisible Unicode-encoded binary payload
hidden in the "relay_config.txt" configuration file.

Usage: python stage3_unicode_decoder.py relay_config.txt

Author: nmluan (solution script)
"""

import struct
import binascii
import sys
import os

# Encoding characters (discovered by reversing the ARM64 loader)
BIT_ZERO = '\uFFA0'   # Hangul Half-Width Filler
BIT_ONE  = '\u3164'    # Hangul Filler
BYTE_DELIM = '\u200D'  # Zero-Width Joiner

TAG_BEGIN = '\U000E0001'  # Language Tag
TAG_END   = '\U000E007F'  # Cancel Tag


def analyze_file(filepath):
    """Analyze a file for invisible Unicode characters."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"[*] File size: {len(content)} chars, {os.path.getsize(filepath)} bytes")
    
    # Count invisible characters
    counts = {}
    for ch in content:
        cp = ord(ch)
        if cp > 0x7F and ch not in '\n\r\t':
            name = f"U+{cp:04X}" if cp < 0x10000 else f"U+{cp:06X}"
            counts[name] = counts.get(name, 0) + 1
    
    if counts:
        print(f"\n[!] Found {sum(counts.values())} non-ASCII characters!")
        print(f"    Character distribution:")
        for name, count in sorted(counts.items(), key=lambda x: -x[1])[:20]:
            print(f"      {name}: {count} occurrences")
    
    return content


def find_tag_region(content):
    """Find the encoded payload region between TAG_BEGIN and TAG_END."""
    start = content.find(TAG_BEGIN)
    end = content.find(TAG_END)
    
    if start == -1:
        print("[!] TAG_BEGIN (U+E0001) not found!")
        return None
    if end == -1:
        print("[!] TAG_END (U+E007F) not found!")
        return None
    
    print(f"[+] Found payload region: chars {start} to {end}")
    return content[start:end + 1]


def extract_crc(region):
    """Extract CRC32 from tag nibble characters."""
    nibbles = []
    for ch in region:
        cp = ord(ch)
        if 0xE0030 <= cp <= 0xE003F:
            nibbles.append(cp - 0xE0030)
    
    if len(nibbles) < 8:
        print(f"[!] Not enough CRC nibbles: {len(nibbles)}")
        return None
    
    # Take first 8 nibbles (from begin tags)
    crc_bytes = bytes([
        (nibbles[0] << 4) | nibbles[1],
        (nibbles[2] << 4) | nibbles[3],
        (nibbles[4] << 4) | nibbles[5],
        (nibbles[6] << 4) | nibbles[7],
    ])
    crc = struct.unpack('>I', crc_bytes)[0]
    print(f"[+] Embedded CRC32: 0x{crc:08X}")
    return crc


def decode_payload(region):
    """Decode the invisible Unicode payload to binary."""
    # Filter to only encoding characters and delimiters
    cleaned = ''
    for ch in region:
        if ch in (BIT_ZERO, BIT_ONE, BYTE_DELIM):
            cleaned += ch
    
    print(f"[+] Filtered payload: {len(cleaned)} encoding chars")
    
    # Split by delimiter
    byte_strings = cleaned.split(BYTE_DELIM)
    
    result = bytearray()
    for bs in byte_strings:
        if len(bs) != 8:
            continue
        val = 0
        for i, ch in enumerate(bs):
            if ch == BIT_ONE:
                val |= (1 << (7 - i))
        result.append(val)
    
    return bytes(result)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <config_file>")
        sys.exit(1)
    
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    filepath = sys.argv[1]
    print(f"=== Stage 3: Invisible Unicode Decoder ===\n")
    
    # Step 1: Analyze the file
    content = analyze_file(filepath)
    
    # Step 2: Find the tagged payload region
    region = find_tag_region(content)
    if region is None:
        print("\n[!] No encoded payload found. Check the file.")
        sys.exit(1)
    
    # Step 3: Extract and verify CRC
    expected_crc = extract_crc(region)
    
    # Step 4: Decode the payload
    payload = decode_payload(region)
    print(f"[+] Decoded payload: {len(payload)} bytes")
    print(f"    First 32 bytes: {payload[:32].hex()}")
    
    # Step 5: Verify CRC
    actual_crc = binascii.crc32(payload) & 0xFFFFFFFF
    print(f"[+] Computed CRC32: 0x{actual_crc:08X}")
    
    if expected_crc and actual_crc == expected_crc:
        print("[+] CRC32 MATCH! Payload integrity verified.")
    else:
        print("[!] CRC32 MISMATCH! Payload may be corrupted.")
    
    # Step 6: Save decoded payload
    output_path = os.path.splitext(filepath)[0] + "_decoded.bin"
    with open(output_path, 'wb') as f:
        f.write(payload)
    print(f"\n[+] Decoded payload saved to: {output_path}")
    print(f"[*] Note: This payload is still encrypted. Proceed to Stage 4 (AVR/VM RE)")
    print(f"    and Stage 5 (cryptanalysis) to decrypt the flag.")


if __name__ == '__main__':
    main()
