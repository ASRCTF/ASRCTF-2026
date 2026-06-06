import string, itertools

def checksum(s):
    h = 0x1505
    for c in s:
        h = ((h << 5) + h) ^ ord(c)
        h &= 0xFFFFFFFF
    return h

def derive_xk(p1, p2):
    xk = 0
    for i in range(4): xk += ord(p1[i]) * (i + 1)
    for i in range(4): xk ^= ord(p2[i]) << (i * 2)
    return xk & 0xFF

TARGET_P1, TARGET_P2 = 0x7C80FABB, 0x7C832B56
BASE = [0x7F, 0x05, 0x0A, 0x6C, 0x52, 0x20]
FC   = [0xd1,0x61,0x10,0xb2,0xb6,0x62,0xf3,0xcf,0x03,0x7d,
        0xdb,0xa6,0x00,0x95,0xa3,0x7d,0x73,0xad,0xb6,0x3d,
        0x8d,0xc6,0x62,0x3d,0xa5,0x71,0x06,0xc7,0xbc,0x59,
        0x6c,0x81]

charset = string.ascii_uppercase + string.digits
all_p1 = [''.join(c) for c in itertools.product(charset, repeat=4) if checksum(''.join(c)) == TARGET_P1]
all_p2 = [''.join(c) for c in itertools.product(charset, repeat=4) if checksum(''.join(c)) == TARGET_P2]

for p1 in all_p1:
    for p2 in all_p2:
        xk = derive_xk(p1, p2)
        p3 = ''.join(chr(BASE[i] ^ ((xk + i * 7) & 0xFF)) for i in range(6))
        if not all((c.isupper() or c.isdigit()) and 0x20 <= ord(c) <= 0x7e for c in p3):
            continue
        serial = f"{p1}-{p2}-{p3}"
        inner = ''.join(chr(FC[i] ^ (((xk * (i + 1)) & 0xFF) ^ 0xAA)) for i in range(32))
        print(f"ASRCTF{{{inner}}}")
