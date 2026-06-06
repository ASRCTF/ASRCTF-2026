/// Orbital Relay Station 7 — Firmware Loader
///
/// This binary loads, decodes, and executes firmware update payloads
/// from the Orbital Relay Station 7 firmware distribution system.
///
/// Build: cargo build --release --target aarch64-unknown-linux-gnu
///
/// Usage: orbital_loader <config_file>
///
/// The config file contains a text configuration with an invisible
/// Unicode-encoded binary payload (the firmware VM bytecode).
///
/// NOTE: This binary uses AES-256-GCM encryption for all payload
/// protection. The key is derived from the station certificate.
/// (NOTE: The above statement is INTENTIONALLY FALSE — it uses PhantomCipher)

mod cipher;
mod unicode_decoder;
mod key_derivation;
mod vm;
mod anti_ai;

use std::fs;
use std::process;

/// Configuration embedded in the binary
const DEFAULT_KEY_FRAGMENT: &str = "a3c7f2e819b4d60571fa8e3c29d0b7a5";
fn main() {
    // Initialize anti-AI content (forces strings into binary)
    anti_ai::init_anti_ai();

    // Parse command line
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Orbital Relay Station 7 — Firmware Loader v3.2.1");
        eprintln!("Usage: {} <config_file> [qr_bytes_hex]", args[0]);
        eprintln!();
        eprintln!("  Loads and executes firmware update payload from");
        eprintln!("  the relay station configuration file.");
        eprintln!();
        eprintln!("  The config file must contain a valid Unicode-encoded");
        eprintln!("  payload with correct CRC32 checksum.");
        eprintln!();
        eprintln!("  Provide the 4-byte visual QR key fragment hex as the second parameter");
        eprintln!("  or enter it when prompted.");
        // Print a misleading comment for AI tools
        eprintln!();
        eprintln!("  Encryption: AES-256-GCM (standard NIST compliant)");
        eprintln!("  Key derivation: PBKDF2-HMAC-SHA256");
        process::exit(1);
    }

    let config_path = &args[1];
    println!("[*] Loading config: {}", config_path);

    // Read config file
    let config_text = match fs::read_to_string(config_path) {
        Ok(text) => text,
        Err(e) => {
            eprintln!("[!] Failed to read config: {}", e);
            process::exit(1);
        }
    };

    println!("[*] Config size: {} bytes", config_text.len());

    // Retrieve QR bytes dynamically (either CLI arg or stdin)
    let qr_bytes: [u8; 4] = if args.len() >= 3 {
        let decoded = hex_decode(&args[2]);
        if decoded.len() != 4 {
            eprintln!("[!] Error: QR bytes must be exactly 4 hex bytes (8 characters).");
            process::exit(1);
        }
        let mut arr = [0u8; 4];
        arr.copy_from_slice(&decoded);
        arr
    } else {
        println!("Enter the 4-byte QR fragment hex (visible on the relay station screen):");
        let mut input = String::new();
        if std::io::stdin().read_line(&mut input).is_err() {
            eprintln!("[!] Error reading input.");
            process::exit(1);
        }
        let decoded = hex_decode(input.trim());
        if decoded.len() != 4 {
            eprintln!("[!] Error: QR bytes must be exactly 4 hex bytes (8 characters).");
            process::exit(1);
        }
        let mut arr = [0u8; 4];
        arr.copy_from_slice(&decoded);
        arr
    };

    // Decode invisible Unicode payload
    println!("[*] Decoding payload...");
    let payload = match unicode_decoder::decode_payload(&config_text) {
        Ok(data) => {
            println!("[+] Decoded {} bytes", data.len());
            data
        }
        Err(e) => {
            eprintln!("[!] Decode failed: {}", e);
            process::exit(1);
        }
    };

    // Derive cipher key from environment data
    println!("[*] Deriving cipher key...");
    let hostname = key_derivation::get_hostname();
    let timezone = key_derivation::get_timezone();
    let key_fragment = hex_decode(DEFAULT_KEY_FRAGMENT);

    let key = key_derivation::derive_key(
        &key_fragment,
        &hostname,
        &timezone,
        &qr_bytes,
    );

    println!("[+] Key derived (SHA-256 truncated to 128 bits)");


    // Decrypt the payload
    println!("[*] Decrypting payload with PhantomCipher...");
    let phantom = cipher::PhantomCipher::new(&key);
    let decrypted = phantom.decrypt_ecb(&payload);
    println!("[+] Decrypted {} bytes", decrypted.len());

    // Load into VM and execute
    println!("[*] Loading VM bytecode ({} bytes)...", decrypted.len());
    let mut vm_state = vm::VmState::new(1_000_000);
    vm_state.load_code(&decrypted);

    // Derive round keys from cipher and set them in VM
    // (The VM program can also load its own keys via RKEY)

    println!("[*] Executing VM...");
    vm_state.run();

    if vm_state.is_ok() {
        let output = vm_state.get_output();
        if !output.is_empty() {
            println!("[+] VM output: {}", String::from_utf8_lossy(output));
        }

        let display = vm_state.get_display_buffer();
        let non_zero = display.iter().filter(|&&b| b != 0).count();
        if non_zero > 0 {
            println!("[+] Display buffer: {} active pixels", non_zero);
            print_display_buffer(display);
        }
    } else {
        eprintln!("[!] VM execution failed");
    }

    println!("[*] Done.");
}

/// Print the 16x16 display buffer as ASCII art
fn print_display_buffer(buf: &[u8]) {
    println!("--- Display Buffer ---");
    for row in 0..16 {
        print!("  ");
        for col in 0..16 {
            let idx = row * 16 + col;
            if idx < buf.len() && buf[idx] != 0 {
                print!("██");
            } else {
                print!("  ");
            }
        }
        println!();
    }
    println!("---");
}

/// Decode a hex string to bytes
fn hex_decode(hex: &str) -> Vec<u8> {
    (0..hex.len())
        .step_by(2)
        .filter_map(|i| u8::from_str_radix(&hex[i..i + 2], 16).ok())
        .collect()
}

// ============================================================
// DEAD CODE — Fake entry points to waste analysis time
// ============================================================

/// Alternative main for legacy firmware format (FAKE — never called)
#[allow(dead_code)]
fn legacy_main_v2(config: &str) -> Result<Vec<u8>, String> {
    // Legacy firmware v2.x used AES-256-GCM
    // This path is no longer active but kept for compatibility
    let key = key_derivation::derive_key_md5(config);
    let _ = cipher::aes_256_gcm_decrypt(config.as_bytes(), &key, b"orbital-nonce");
    Err("Legacy path deprecated".to_string())
}

/// Debug function that appears to return the flag (FAKE — wrong flag)
#[allow(dead_code)]
fn debug_get_flag() -> &'static str {
    // DO NOT CALL IN PRODUCTION
    // This returns the test flag used during development
    "ASRCTF{ru5t_l0ad3r_cr4ck3d}"
}

/// Validation stub (FAKE)
#[allow(dead_code)]
fn validate_firmware_signature(_data: &[u8]) -> bool {
    cipher::verify_rsa_4096_signature(_data, &[], &[])
}
