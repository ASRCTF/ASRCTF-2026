#!/usr/bin/env python3
"""
Custom Block Cipher for phantom_firmware CTF challenge.

PhantomCipher: 64-bit block, 128-bit key, 16-round Feistel network
with an intentionally weak S-box that enables differential cryptanalysis.

The round function uses a Substitution-Permutation Network (SPN):
  1. Split 32-bit half-block into 8 nibbles
  2. Apply weak 4-bit S-box to each nibble  
  3. Apply fixed bit permutation (P-box)
  4. XOR with round key

Key schedule: simple rotation + XOR with round constants.

Author: nmluan (challenge build tooling)
"""

import struct
import hashlib

# Weak S-box with differential characteristic:
# DDT[0x0D][0x07] = 1 (probability 2^-4)
SBOX = [0x0C, 0x05, 0x06, 0x0B, 0x09, 0x00, 0x0A, 0x0D,
        0x03, 0x0E, 0x0F, 0x08, 0x04, 0x07, 0x01, 0x02]

SBOX_INV = [0x05, 0x0E, 0x0F, 0x08, 0x0C, 0x01, 0x02, 0x0D,
            0x0B, 0x04, 0x06, 0x03, 0x00, 0x07, 0x09, 0x0A]

# P-box: bit permutation for 32-bit values
# Maps bit i to bit PBOX[i]
PBOX = [0,  8, 16, 24,  1,  9, 17, 25,
        2, 10, 18, 26,  3, 11, 19, 27,
        4, 12, 20, 28,  5, 13, 21, 29,
        6, 14, 22, 30,  7, 15, 23, 31]

# Inverse P-box
PBOX_INV = [0] * 32
for i, p in enumerate(PBOX):
    PBOX_INV[p] = i

# Round constants for key schedule
ROUND_CONSTANTS = [
    0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344,
    0xA4093822, 0x299F31D0, 0x082EFA98, 0xEC4E6C89,
    0x452821E6, 0x38D01377, 0xBE5466CF, 0x34E90C6C,
    0xC0AC29B7, 0xC97C50DD, 0x3F84D5B5, 0xB5470917,
]


def apply_sbox_32(val, sbox):
    """Apply 4-bit S-box to each nibble of a 32-bit value."""
    result = 0
    for i in range(8):
        nibble = (val >> (i * 4)) & 0xF
        result |= sbox[nibble] << (i * 4)
    return result


def apply_pbox_32(val, pbox):
    """Apply bit permutation to a 32-bit value."""
    result = 0
    for i in range(32):
        if val & (1 << i):
            result |= 1 << pbox[i]
    return result


def rotate_left_32(val, n):
    """Rotate a 32-bit value left by n bits."""
    n = n % 32
    return ((val << n) | (val >> (32 - n))) & 0xFFFFFFFF


class PhantomCipher:
    """
    PhantomCipher: 64-bit block, 128-bit key, 16-round Feistel network.
    """
    
    def __init__(self, key):
        """
        Initialize with a 128-bit (16-byte) key.
        """
        if isinstance(key, (bytes, bytearray)):
            if len(key) != 16:
                raise ValueError(f"Key must be 16 bytes, got {len(key)}")
            self.master_key = key
        else:
            raise TypeError("Key must be bytes")
        
        self.round_keys = self._key_schedule()
    
    def _key_schedule(self):
        """
        Derive 16 32-bit round keys from the 128-bit master key.
        
        Method: Split key into two 64-bit halves, rotate and XOR with round constants.
        """
        k_hi = struct.unpack('>Q', self.master_key[:8])[0]
        k_lo = struct.unpack('>Q', self.master_key[8:])[0]
        
        round_keys = []
        for i in range(16):
            # Combine halves with round constant
            rk = ((k_hi >> 32) ^ (k_lo & 0xFFFFFFFF) ^ ROUND_CONSTANTS[i]) & 0xFFFFFFFF
            round_keys.append(rk)
            
            # Rotate key material for next round
            k_hi = rotate_left_32(k_hi & 0xFFFFFFFF, 5) | (rotate_left_32(k_hi >> 32, 3) << 32)
            k_lo = rotate_left_32(k_lo & 0xFFFFFFFF, 7) | (rotate_left_32(k_lo >> 32, 11) << 32)
            k_hi ^= k_lo
        
        return round_keys
    
    def _round_function(self, half_block, round_key):
        """
        Feistel round function F(x, K):
        1. S-box substitution on each nibble
        2. P-box permutation
        3. XOR with round key
        """
        # Apply S-box
        x = apply_sbox_32(half_block, SBOX)
        
        # Apply P-box
        x = apply_pbox_32(x, PBOX)
        
        # XOR with round key
        x = x ^ round_key
        
        return x
    
    def _round_function_inv(self, half_block, round_key):
        """
        Inverse round function F^-1(x, K):
        Note: In Feistel, we don't actually need this for decryption,
        we just run rounds in reverse. But useful for analysis.
        """
        x = half_block ^ round_key
        x = apply_pbox_32(x, PBOX_INV)
        x = apply_sbox_32(x, SBOX_INV)
        return x
    
    def encrypt_block(self, plaintext):
        """
        Encrypt a single 64-bit (8-byte) block.
        
        Standard Feistel: each round does L, R = R, L ^ F(R, K_i)
        Output is (R, L) after last round (no final swap needed if
        decrypt applies same structure in reverse).
        """
        if len(plaintext) != 8:
            raise ValueError(f"Block must be 8 bytes, got {len(plaintext)}")
        
        # Split into two 32-bit halves
        L = struct.unpack('>I', plaintext[:4])[0]
        R = struct.unpack('>I', plaintext[4:])[0]
        
        # 16 Feistel rounds
        for i in range(16):
            tmp = R
            R = L ^ self._round_function(R, self.round_keys[i])
            L = tmp
        
        # Output with swap (standard Feistel convention)
        return struct.pack('>II', R, L)
    
    def decrypt_block(self, ciphertext):
        """
        Decrypt a single 64-bit (8-byte) block.
        
        Reverse the encryption: undo the final swap, then run rounds
        in reverse order with the same Feistel structure.
        """
        if len(ciphertext) != 8:
            raise ValueError(f"Block must be 8 bytes, got {len(ciphertext)}")
        
        # Undo the final swap from encryption
        R = struct.unpack('>I', ciphertext[:4])[0]
        L = struct.unpack('>I', ciphertext[4:])[0]
        
        # 16 Feistel rounds in reverse order
        for i in range(15, -1, -1):
            tmp = L
            L = R ^ self._round_function(L, self.round_keys[i])
            R = tmp
        
        return struct.pack('>II', L, R)
    
    def get_round_keys_bytes(self):
        """Get round keys as a list of 4-byte arrays (for VM)."""
        result = []
        for rk in self.round_keys:
            result.append(struct.pack('>I', rk))
        return result


def encrypt_flag(flag_str, key_bytes):
    """Encrypt a flag string with PKCS#7 padding."""
    cipher = PhantomCipher(key_bytes)
    
    # PKCS#7 padding
    data = flag_str.encode('utf-8')
    pad_len = 8 - (len(data) % 8)
    data += bytes([pad_len] * pad_len)
    
    # ECB mode (each 8-byte block encrypted independently)
    ciphertext = b''
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        ciphertext += cipher.encrypt_block(block)
    
    return ciphertext


def decrypt_flag(ciphertext, key_bytes):
    """Decrypt a flag ciphertext and remove PKCS#7 padding."""
    cipher = PhantomCipher(key_bytes)
    
    plaintext = b''
    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i:i+8]
        plaintext += cipher.decrypt_block(block)
    
    # Remove PKCS#7 padding
    pad_val = plaintext[-1]
    if 1 <= pad_val <= 8 and all(b == pad_val for b in plaintext[-pad_val:]):
        plaintext = plaintext[:-pad_val]
    
    return plaintext.decode('utf-8')


if __name__ == '__main__':
    print("=== PhantomCipher Test Suite ===\n")
    
    # Test 1: Basic encrypt/decrypt roundtrip
    key = bytes.fromhex('0123456789ABCDEF0123456789ABCDEF')
    cipher = PhantomCipher(key)
    
    plaintext = b'TESTTEST'
    ct = cipher.encrypt_block(plaintext)
    pt = cipher.decrypt_block(ct)
    assert pt == plaintext, f"Roundtrip failed: {pt} != {plaintext}"
    print(f"[+] Test 1 (roundtrip): PASS")
    print(f"    PT: {plaintext.hex()}")
    print(f"    CT: {ct.hex()}")
    print(f"    DT: {pt.hex()}")
    
    # Test 2: Different keys produce different ciphertexts
    key2 = bytes.fromhex('FEDCBA9876543210FEDCBA9876543210')
    cipher2 = PhantomCipher(key2)
    ct2 = cipher2.encrypt_block(plaintext)
    assert ct != ct2, "Different keys produced same ciphertext!"
    print(f"\n[+] Test 2 (key sensitivity): PASS")
    print(f"    CT1: {ct.hex()}")
    print(f"    CT2: {ct2.hex()}")
    
    # Test 3: Avalanche effect
    pt1 = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    pt2 = b'\x00\x00\x00\x00\x00\x00\x00\x01'
    ct1 = cipher.encrypt_block(pt1)
    ct2_aval = cipher.encrypt_block(pt2)
    diff_bits = bin(int.from_bytes(ct1, 'big') ^ int.from_bytes(ct2_aval, 'big')).count('1')
    print(f"\n[+] Test 3 (avalanche): {diff_bits}/64 bits differ")
    print(f"    CT1: {ct1.hex()}")
    print(f"    CT2: {ct2_aval.hex()}")
    
    # Test 4: Flag encryption
    FLAG = "ASRCTF{gh0st_1n_th3_sh3ll_0f_orb1t4l_d3c4y}"
    
    # Derive key from challenge parameters
    key_fragment = "a3c7f2e819b4d60571fa8e3c29d0b7a5"
    hostname = "orbital-relay-7"
    timezone = "UTC"
    qr_bytes = bytes([0xDE, 0xAD, 0xBE, 0xEF])
    
    material = bytes.fromhex(key_fragment) + hostname.encode() + timezone.encode() + qr_bytes
    master_key = hashlib.sha256(material).digest()[:16]
    
    ct_flag = encrypt_flag(FLAG, master_key)
    dt_flag = decrypt_flag(ct_flag, master_key)
    
    assert dt_flag == FLAG, f"Flag roundtrip failed: {dt_flag} != {FLAG}"
    print(f"\n[+] Test 4 (flag encryption): PASS")
    print(f"    Master key: {master_key.hex()}")
    print(f"    Flag: {FLAG}")
    print(f"    Ciphertext ({len(ct_flag)} bytes): {ct_flag.hex()}")
    print(f"    Decrypted: {dt_flag}")
    
    # Test 5: Round keys
    round_keys = cipher.get_round_keys_bytes()
    print(f"\n[+] Round keys for master key {key.hex()}:")
    for i, rk in enumerate(round_keys):
        print(f"    Round {i:2d}: {rk.hex()}")
    
    # Test 6: S-box verification
    print(f"\n[+] Test 6 (S-box weakness verification):")
    count = 0
    for x in range(16):
        dy = SBOX[x ^ 0x0D] ^ SBOX[x]
        if dy == 0x07:
            count += 1
            print(f"    x=0x{x:X}: S(0x{x:X})=0x{SBOX[x]:X}, S(0x{x^0xD:X})=0x{SBOX[x^0xD]:X}, diff=0x{dy:X}")
    print(f"    Total: {count}/16 (probability 2^-4)")
    assert count >= 1, "S-box weakness not present!"
    
    print(f"\n=== All tests passed! ===")
