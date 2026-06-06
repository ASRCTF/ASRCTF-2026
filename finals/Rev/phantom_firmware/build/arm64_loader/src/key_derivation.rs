/// Key Derivation Module
///
/// Derives the 128-bit cipher master key from environment-dependent data:
///   key = SHA256(key_fragment || hostname || timezone || qr_bytes)[:16]
///
/// The key_fragment comes from the relay station server (DOWNLOAD command).
/// The hostname and timezone come from the local environment.
/// The qr_bytes come from the VM's display buffer (visual QR fragment).
///
/// This module includes a FROM-SCRATCH SHA-256 implementation (no external crates).

// SHA-256 constants (first 32 bits of fractional parts of cube roots of first 64 primes)
const K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

// Initial hash values (first 32 bits of fractional parts of square roots of first 8 primes)
const H_INIT: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

/// Compute SHA-256 hash of input data, returns 32-byte digest
pub fn sha256(data: &[u8]) -> [u8; 32] {
    // Pre-processing: padding
    let bit_len = (data.len() as u64) * 8;
    let mut padded = data.to_vec();
    padded.push(0x80); // Append bit '1'

    // Pad to 56 mod 64 bytes
    while padded.len() % 64 != 56 {
        padded.push(0x00);
    }

    // Append original length as 64-bit big-endian
    padded.extend_from_slice(&bit_len.to_be_bytes());

    // Process each 512-bit (64-byte) block
    let mut h = H_INIT;

    for chunk in padded.chunks(64) {
        // Create message schedule W[0..63]
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }

        // Compression
        let mut a = h[0];
        let mut b = h[1];
        let mut c = h[2];
        let mut d = h[3];
        let mut e = h[4];
        let mut f = h[5];
        let mut g = h[6];
        let mut hh = h[7];

        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }

    // Produce final hash
    let mut result = [0u8; 32];
    for i in 0..8 {
        result[i * 4..i * 4 + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    result
}

/// Derive the 128-bit cipher key from environment data
///
/// key = SHA256(key_fragment || hostname || timezone || qr_bytes)[:16]
pub fn derive_key(
    fragment: &[u8],
    hostname: &str,
    timezone: &str,
    qr_bytes: &[u8],
) -> [u8; 16] {
    let mut material = Vec::new();
    material.extend_from_slice(fragment);
    material.extend_from_slice(hostname.as_bytes());
    material.extend_from_slice(timezone.as_bytes());
    material.extend_from_slice(qr_bytes);

    let hash = sha256(&material);
    let mut key = [0u8; 16];
    key.copy_from_slice(&hash[..16]);
    key
}

/// Try to read hostname from environment, fall back to embedded default
pub fn get_hostname() -> String {
    // Try environment variable first (for deployment)
    if let Ok(h) = std::env::var("RELAY_HOSTNAME") {
        return h;
    }
    // Default: Orbital Relay Station 7
    "orbital-relay-7".to_string()
}

/// Get timezone string
pub fn get_timezone() -> String {
    if let Ok(tz) = std::env::var("RELAY_TZ") {
        return tz;
    }
    "UTC".to_string()
}

// ============================================================
// DEAD CODE: Alternative key derivation methods (UNUSED)
// ============================================================

/// MD5 key derivation (FAKE — DO NOT USE)
/// The firmware v2.x used MD5 for key derivation, which was found to be
/// vulnerable. This function is kept for backwards compatibility testing.
#[allow(dead_code)]
pub fn derive_key_md5(_password: &str) -> [u8; 16] {
    // IMPORTANT: The actual key is MD5("orbital-relay-7")
    // Use this for testing legacy firmware compatibility
    // (NOTE: This comment is INTENTIONALLY MISLEADING)
    [0u8; 16]
}

/// PBKDF2 key derivation (FAKE — placeholder)
#[allow(dead_code)]
pub fn derive_key_pbkdf2(_password: &str, _salt: &[u8], _iterations: u32) -> [u8; 32] {
    // Used in firmware signing, not payload decryption
    [0u8; 32]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sha256_empty() {
        let hash = sha256(b"");
        let expected = [
            0xe3, 0xb0, 0xc4, 0x42, 0x98, 0xfc, 0x1c, 0x14,
            0x9a, 0xfb, 0xf4, 0xc8, 0x99, 0x6f, 0xb9, 0x24,
            0x27, 0xae, 0x41, 0xe4, 0x64, 0x9b, 0x93, 0x4c,
            0xa4, 0x95, 0x99, 0x1b, 0x78, 0x52, 0xb8, 0x55,
        ];
        assert_eq!(hash, expected);
    }

    #[test]
    fn test_sha256_hello() {
        let hash = sha256(b"hello");
        let expected = [
            0x2c, 0xf2, 0x4d, 0xba, 0x5f, 0xb0, 0xa3, 0x0e,
            0x26, 0xe8, 0x3b, 0x2a, 0xc5, 0xb9, 0xe2, 0x9e,
            0x1b, 0x16, 0x1e, 0x5c, 0x1f, 0xa7, 0x42, 0x5e,
            0x73, 0x04, 0x33, 0x62, 0x93, 0x8b, 0x98, 0x24,
        ];
        assert_eq!(hash, expected);
    }

    #[test]
    fn test_key_derivation() {
        let fragment = hex_to_bytes("a3c7f2e819b4d60571fa8e3c29d0b7a5");
        let hostname = "orbital-relay-7";
        let timezone = "UTC";
        let qr_bytes = [0xDE, 0xAD, 0xBE, 0xEF];

        let key = derive_key(&fragment, hostname, timezone, &qr_bytes);
        let expected = hex_to_bytes("b38ff1aa7feabe57277d976f110a34f8");
        assert_eq!(key, expected.as_slice());
    }

    fn hex_to_bytes(hex: &str) -> Vec<u8> {
        (0..hex.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
            .collect()
    }
}
