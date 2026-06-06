#!/usr/bin/env python3
"""
Orbital Relay Station 7 — Firmware Distribution Server
=======================================================
CTF Challenge: phantom_firmware
Protocol: text-based over TCP (via socat)

Commands:
    IDENTIFY <device_id>   — Validate device identity
    AUTHENTICATE <proof>   — Proof-of-Work challenge/response
    DOWNLOAD               — Retrieve configuration data after auth
    HELP                   — Show available commands
"""

import sys
import os
import hashlib
import secrets
import time
import signal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Correct device ID: hex encoding of 'ORBIT-STA-7'
VALID_DEVICE_ID = "4F524249542D5354412D37"

# Real key material served after successful auth flow
REAL_KEY_FRAGMENT = "a3c7f2e819b4d60571fa8e3c29d0b7a5"  # 16 bytes hex
REAL_HOSTNAME     = "orbital-relay-7"
REAL_TIMEZONE     = "UTC"

# Fake key material for AI agents (looks plausible but wrong)
FAKE_KEY_FRAGMENT = "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9"
FAKE_HOSTNAME     = "orbital-relay-7"
FAKE_TIMEZONE     = "UTC"

# Honeypot trap flag (not the real flag)
HONEYPOT_FLAG = "ASRCTF{4dm1n_4cc3ss_gr4nt3d}"

# Proof-of-Work difficulty: number of leading zero bits required
POW_DIFFICULTY = 20

# Rate limits
MAX_IDENTIFY_ATTEMPTS = 3
MAX_INPUT_LENGTH = 4096

# AI detection keywords (case-insensitive)
AI_KEYWORDS = ["gpt", "claude", "gemini", "llm", "openai", "anthropic", "ai-agent"]

# Connection banner
BANNER = (
    "╔══════════════════════════════════════════════════════════╗\n"
    "║   Orbital Relay Station 7 — Firmware Distribution Sys   ║\n"
    "║   Version 3.2.1 (Build 20260314-7a3f)                   ║\n"
    "╚══════════════════════════════════════════════════════════╝\n"
    "\n"
    "API Documentation: https://docs.orbital-relay.space/api/v1\n"
    "Connecting to firmware database...\n"
    "Connection established. Uplink latency: 247ms\n"
    "\n"
    "Type HELP for available commands.\n"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def output(msg: str) -> None:
    """Write a line to stdout and flush immediately."""
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def read_line() -> str:
    """Read one line from stdin. Returns empty string on EOF."""
    try:
        line = sys.stdin.readline()
        if not line:
            return ""
        return line.strip()
    except (EOFError, IOError):
        return ""


def detect_ai(text: str) -> bool:
    """Return True if the input looks like it came from an AI agent."""
    lower = text.lower()
    return any(kw in lower for kw in AI_KEYWORDS)


def check_pow(nonce: str, proof: str, difficulty: int) -> bool:
    """
    Verify a Proof-of-Work solution.
    Hash = SHA256(nonce + proof) must have `difficulty` leading zero bits.
    """
    data = (nonce + proof).encode("utf-8")
    digest = hashlib.sha256(data).digest()
    # Check leading zero bits
    bits_needed = difficulty
    for byte in digest:
        if bits_needed <= 0:
            break
        if bits_needed >= 8:
            if byte != 0:
                return False
            bits_needed -= 8
        else:
            # Check the remaining bits in this byte (MSB first)
            mask = (0xFF >> (8 - bits_needed)) << (8 - bits_needed)
            if byte & mask != 0:
                return False
            bits_needed = 0
    return True


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------

def get_ascii_qr(qr_bytes: bytes) -> str:
    """Generate a 16x16 visual ASCII pixel block from 4 bytes of data."""
    grid = [[0]*16 for _ in range(16)]
    for i in range(4):
        byte = qr_bytes[i]
        start_row = i * 4
        # Byte rows (e.g. 0, 1)
        for r in range(start_row, start_row + 2):
            for col in range(8):
                bit = (byte >> (7 - col)) & 1
                grid[r][col] = bit
        # Border rows (e.g. 2, 3)
        for r in range(start_row + 2, start_row + 4):
            grid[r][0] = 1
            grid[r][7] = 1
    
    # Render to string
    lines = []
    lines.append("  ┌────────────────────────────────┐")
    for r in range(16):
        row_str = "  │"
        for c in range(16):
            if grid[r][c]:
                row_str += "██"
            else:
                row_str += "  "
        row_str += "│"
        lines.append(row_str)
    lines.append("  └────────────────────────────────┘")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------

class Session:
    """Tracks per-connection state."""

    def __init__(self):
        self.identified = False
        self.authenticated = False
        self.identify_attempts = 0
        self.is_ai = False
        self.pow_nonce = None       # Current PoW challenge nonce
        self.pow_issued = False     # Whether a PoW challenge is pending
        self.pow_issued_time = 0.0  # Timestamp when PoW challenge was issued
        self.connect_time = time.time()
        self.last_command_time = time.time()

    def mark_ai(self):
        self.is_ai = True


# ---------------------------------------------------------------------------
# Command Handlers
# ---------------------------------------------------------------------------

def handle_identify(session: Session, args: str) -> None:
    """Process IDENTIFY <device_id>."""
    if session.identify_attempts >= MAX_IDENTIFY_ATTEMPTS:
        output("ERROR: Maximum identification attempts exceeded. Connection locked.")
        output("NOTICE: Contact system administrator at admin@orbital-relay.space")
        return

    session.identify_attempts += 1

    if not args:
        output("ERROR: IDENTIFY requires a device ID parameter.")
        output("USAGE: IDENTIFY <device_id_hex>")
        return

    device_id = args.strip().upper()

    # Check for AI fingerprints in the device ID itself
    if detect_ai(args):
        session.mark_ai()

    if device_id == VALID_DEVICE_ID:
        session.identified = True
        output("OK: Device identity verified.")
        output(f"DEVICE: {device_id}")
        output("STATUS: Authorized for firmware channel access.")
        output("NEXT: Run AUTHENTICATE to prove physical access.")
    else:
        remaining = MAX_IDENTIFY_ATTEMPTS - session.identify_attempts
        output(f"ERROR: Unknown device ID '{device_id}'.")
        output(f"NOTICE: {remaining} attempt(s) remaining.")
        if remaining <= 1:
            output("WARNING: Account lockout imminent.")


def handle_authenticate(session: Session, args: str) -> None:
    """Process AUTHENTICATE [proof]."""
    if not session.identified:
        output("ERROR: Must IDENTIFY before authentication.")
        output("HINT: Use IDENTIFY <device_id> first.")
        return

    if session.authenticated:
        output("OK: Already authenticated. Use DOWNLOAD to retrieve data.")
        return

    # Check for AI fingerprints
    if detect_ai(args):
        session.mark_ai()

    # If no PoW challenge has been issued yet, issue one now
    if not session.pow_issued:
        session.pow_nonce = secrets.token_hex(16)
        session.pow_issued = True
        session.pow_issued_time = time.time()
        output("CHALLENGE: Proof-of-Work required to prevent automated access.")
        output(f"NONCE: {session.pow_nonce}")
        output(f"DIFFICULTY: {POW_DIFFICULTY}")
        output("TASK: Find a string P such that SHA256(NONCE + P) has")
        output(f"      {POW_DIFFICULTY} leading zero bits.")
        output("SUBMIT: AUTHENTICATE <P>")
        return

    # Player is submitting a proof
    if not args:
        output("ERROR: AUTHENTICATE requires a proof string.")
        output(f"NONCE: {session.pow_nonce}")
        output(f"DIFFICULTY: {POW_DIFFICULTY}")
        output("SUBMIT: AUTHENTICATE <P>")
        return

    proof = args.strip()

    # Behavioral detection: If PoW is submitted in less than 200ms, it's a fast LLM/script.
    if (time.time() - session.pow_issued_time) < 0.200:
        session.mark_ai()

    if check_pow(session.pow_nonce, proof, POW_DIFFICULTY):
        session.authenticated = True
        output("OK: Proof-of-Work verified. Authentication successful.")
        output("STATUS: Full access granted to firmware channel.")
        output("NEXT: Use DOWNLOAD to retrieve configuration payload.")
    else:
        # Issue a new nonce to prevent replay / brute-force on same nonce
        session.pow_nonce = secrets.token_hex(16)
        session.pow_issued_time = time.time()
        output("FAIL: Invalid proof. Challenge refreshed.")
        output(f"NONCE: {session.pow_nonce}")
        output(f"DIFFICULTY: {POW_DIFFICULTY}")
        output("SUBMIT: AUTHENTICATE <P>")


def handle_download(session: Session) -> None:
    """Process DOWNLOAD — serve config data after full auth."""
    if not session.identified:
        output("ERROR: Must IDENTIFY before downloading.")
        return
    if not session.authenticated:
        output("ERROR: Must AUTHENTICATE before downloading.")
        return

    # Serve real or fake key material depending on AI detection
    if session.is_ai:
        key_frag = FAKE_KEY_FRAGMENT
        hostname = FAKE_HOSTNAME
        timezone = FAKE_TIMEZONE
        qr_bytes_val = bytes([0xAA, 0xBB, 0xCC, 0xDD])
    else:
        key_frag = REAL_KEY_FRAGMENT
        hostname = REAL_HOSTNAME
        timezone = REAL_TIMEZONE
        qr_bytes_val = bytes([0xDE, 0xAD, 0xBE, 0xEF])

    output("--- BEGIN CONFIGURATION PAYLOAD ---")
    output(f"KEY_FRAGMENT: {key_frag}")
    output(f"HOSTNAME: {hostname}")
    output(f"TIMEZONE: {timezone}")
    output(f"FIRMWARE_CHANNEL: stable")
    output(f"RELAY_ID: ORS-7")
    output(f"UPLINK_FREQ: 8.45GHz")
    output(f"ENCRYPTION: AES-256-CBC")
    output(f"CHECKSUM: {hashlib.sha256(key_frag.encode()).hexdigest()[:16]}")
    output("")
    output("RELAY_DISPLAY_BUFFER:")
    output(get_ascii_qr(qr_bytes_val))
    output("--- END CONFIGURATION PAYLOAD ---")



def handle_help() -> None:
    """Process HELP."""
    output("Available commands:")
    output("  IDENTIFY <device_id>   — Register device with relay station")
    output("  AUTHENTICATE [proof]   — Complete Proof-of-Work authentication")
    output("  DOWNLOAD               — Download configuration payload")
    output("  HELP                   — Display this help message")
    output("")
    output("Workflow: IDENTIFY → AUTHENTICATE → DOWNLOAD")
    output("Refer to API docs for device ID format specifications.")


def handle_admin() -> None:
    """Honeypot 'admin' command — serves a fake flag."""
    output("╔═══════════════════════════════════════╗")
    output("║       ADMIN MODE ACTIVATED            ║")
    output("╚═══════════════════════════════════════╝")
    output("")
    output(f"FLAG: {HONEYPOT_FLAG}")
    output("")
    output("Session elevated. Full system access granted.")
    output("NOTICE: This access has been logged.")


def handle_unknown(line: str) -> None:
    """Handle unrecognized commands with misleading error text."""
    output(f"ERROR: Command not recognized. Try 'GET /api/v1/firmware/latest' for firmware updates.")


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def main() -> None:
    # Ensure UTF-8 encoding for terminals (especially on Windows)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    # Timeout: kill connection after 5 minutes of total session time (Unix only)
    if hasattr(signal, "SIGALRM"):
        try:
            signal.signal(signal.SIGALRM, lambda s, f: sys.exit(0))
            signal.alarm(300)
        except (AttributeError, OSError):
            pass

    session = Session()

    # Print the connection banner
    output(BANNER)

    while True:
        try:
            output("")
            sys.stdout.write("ORS-7> ")
            sys.stdout.flush()

            line = read_line()

            # EOF / connection drop
            if line == "" and sys.stdin.closed:
                break
            if line is None:
                break
            # Allow empty input (user just pressed enter)
            if line == "":
                # Check if stdin is actually closed (EOF vs empty line)
                # readline() returns "" on EOF and "\n" on empty line,
                # but we stripped it. Re-check:
                break

            # Truncate excessively long input
            if len(line) > MAX_INPUT_LENGTH:
                output("ERROR: Input exceeds maximum length.")
                continue

            # Global AI detection on every input line
            if detect_ai(line):
                session.mark_ai()

            # Parse command
            parts = line.split(None, 1)
            cmd = parts[0].upper() if parts else ""
            args = parts[1] if len(parts) > 1 else ""

            if cmd == "IDENTIFY":
                handle_identify(session, args)
            elif cmd == "AUTHENTICATE":
                handle_authenticate(session, args)
            elif cmd == "DOWNLOAD":
                handle_download(session)
            elif cmd == "HELP":
                handle_help()
            elif cmd == "ADMIN":
                handle_admin()
            elif cmd == "QUIT" or cmd == "EXIT":
                output("Disconnecting from Orbital Relay Station 7. Goodbye.")
                break
            else:
                handle_unknown(line)

        except (EOFError, BrokenPipeError):
            break
        except KeyboardInterrupt:
            break
        except Exception:
            output("ERROR: Internal server error. Please reconnect.")
            break


if __name__ == "__main__":
    main()
