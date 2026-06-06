import sys

def lfsr_stream(n):
    reg = 0xACE1
    out = []
    for _ in range(n):
        byte = 0
        for b in range(8):
            lsb = reg & 1
            reg = (reg >> 1) ^ (0xB400 if lsb else 0)
            byte = (byte >> 1) | (lsb << 7)
        out.append(byte & 0xFF)
    return out

flag = sys.argv[1].encode()
stream = lfsr_stream(len(flag))
blob = [f ^ k for f, k in zip(flag, stream)]
print(",".join(hex(b) for b in blob))
