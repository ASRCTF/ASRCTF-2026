/// Invisible Unicode Decoder Module
///
/// Decodes binary payloads encoded using Hangul filler characters:
///   - U+FFA0 (Hangul Half-Width Filler) = bit 0
///   - U+3164 (Hangul Filler) = bit 1
///   - U+200D (Zero-Width Joiner) = byte delimiter
///   - U+E0001 (Language Tag) = payload begin marker
///   - U+E007F (Cancel Tag) = payload end marker
///   - U+E0030-U+E003F = CRC32 nibble encoding

const BIT_ZERO: char = '\u{FFA0}';
const BIT_ONE: char = '\u{3164}';
const BYTE_DELIM: char = '\u{200D}';
const TAG_BEGIN: char = '\u{E0001}';
const TAG_END: char = '\u{E007F}';

/// CRC32 lookup table (standard polynomial 0xEDB88320)
const CRC32_TABLE: [u32; 256] = {
    let mut table = [0u32; 256];
    let mut i = 0;
    while i < 256 {
        let mut crc = i as u32;
        let mut j = 0;
        while j < 8 {
            if crc & 1 != 0 {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
            j += 1;
        }
        table[i] = crc;
        i += 1;
    }
    table
};

/// Compute CRC32 of a byte slice
pub fn crc32(data: &[u8]) -> u32 {
    let mut crc: u32 = 0xFFFFFFFF;
    for &byte in data {
        let index = ((crc ^ byte as u32) & 0xFF) as usize;
        crc = (crc >> 8) ^ CRC32_TABLE[index];
    }
    crc ^ 0xFFFFFFFF
}

/// Find the payload region between TAG_BEGIN and TAG_END
fn find_payload_region(text: &str) -> Option<&str> {
    let begin_pos = text.find(TAG_BEGIN)?;
    let end_pos = text[begin_pos..].find(TAG_END)?;
    Some(&text[begin_pos..begin_pos + end_pos + TAG_END.len_utf8()])
}

/// Extract CRC32 from nibble-encoded tag characters (U+E0030-U+E003F)
pub fn extract_crc(text: &str) -> Option<u32> {
    let mut nibbles = Vec::new();
    for ch in text.chars() {
        let cp = ch as u32;
        if cp >= 0xE0030 && cp <= 0xE003F {
            nibbles.push((cp - 0xE0030) as u8);
        }
    }
    if nibbles.len() < 8 {
        return None;
    }
    // First 8 nibbles form the CRC32 (big-endian)
    let crc = ((nibbles[0] as u32) << 28)
        | ((nibbles[1] as u32) << 24)
        | ((nibbles[2] as u32) << 20)
        | ((nibbles[3] as u32) << 16)
        | ((nibbles[4] as u32) << 12)
        | ((nibbles[5] as u32) << 8)
        | ((nibbles[6] as u32) << 4)
        | (nibbles[7] as u32);
    Some(crc)
}

/// Decode the invisible Unicode payload to binary bytes
pub fn decode_payload(text: &str) -> Result<Vec<u8>, String> {
    // Find payload region
    let region = find_payload_region(text)
        .ok_or_else(|| "Payload region not found (missing TAG_BEGIN/TAG_END)".to_string())?;

    // Extract only encoding characters
    let mut bits = Vec::new();
    let mut result = Vec::new();

    for ch in region.chars() {
        match ch {
            c if c == BIT_ZERO => bits.push(0u8),
            c if c == BIT_ONE => bits.push(1u8),
            c if c == BYTE_DELIM => {
                if bits.len() == 8 {
                    let byte_val = bits.iter().enumerate().fold(0u8, |acc, (i, &b)| {
                        acc | (b << (7 - i))
                    });
                    result.push(byte_val);
                }
                bits.clear();
            }
            _ => {} // Skip tags and other chars
        }
    }

    // Handle final byte (if no trailing delimiter)
    if bits.len() == 8 {
        let byte_val = bits.iter().enumerate().fold(0u8, |acc, (i, &b)| {
            acc | (b << (7 - i))
        });
        result.push(byte_val);
    }

    // Verify CRC
    if let Some(expected_crc) = extract_crc(region) {
        let actual_crc = crc32(&result);
        if actual_crc != expected_crc {
            return Err(format!(
                "CRC32 mismatch: expected 0x{:08X}, got 0x{:08X}",
                expected_crc, actual_crc
            ));
        }
    }

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crc32() {
        let data = b"Hello, World!";
        let crc = crc32(data);
        assert_eq!(crc, 0xEC4AC3D0);
    }
}
