import sys
from pathlib import Path

LCG_SEED = 0xDEADC0DE
LCG_MUL  = 1664525
LCG_ADD  = 1013904223
MASK32   = 0xFFFF_FFFF
KEY_LEN  = 28


def lcg_keystream(length):
    state = LCG_SEED
    stream = []
    for _ in range(length):
        state = (state * LCG_MUL + LCG_ADD) & MASK32
        stream.append((state >> 16) & 0xFF)
    return stream


def extract_rodata(path):
    raw = path.read_bytes()
    e_shoff    = int.from_bytes(raw[0x28:0x30], "little")
    e_shentsize = int.from_bytes(raw[0x3A:0x3C], "little")
    e_shnum    = int.from_bytes(raw[0x3C:0x3E], "little")
    e_shstrndx = int.from_bytes(raw[0x3E:0x40], "little")
    str_hdr    = e_shoff + e_shstrndx * e_shentsize
    str_off    = int.from_bytes(raw[str_hdr + 0x18:str_hdr + 0x20], "little")
    for i in range(e_shnum):
        hdr  = e_shoff + i * e_shentsize
        noff = int.from_bytes(raw[hdr:hdr + 4], "little")
        name = raw[str_off + noff: str_off + noff + 16].split(b"\x00")[0]
        if name == b".rodata":
            off  = int.from_bytes(raw[hdr + 0x18:hdr + 0x20], "little")
            size = int.from_bytes(raw[hdr + 0x20:hdr + 0x28], "little")
            return raw[off: off + size]
    raise ValueError(".rodata not found")


def main():
    binary = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("crackme")
    rodata = extract_rodata(binary)
    stream = lcg_keystream(KEY_LEN)
    for start in range(len(rodata) - KEY_LEN + 1):
        candidate = bytes(rodata[start + i] ^ stream[i] for i in range(KEY_LEN))
        if candidate.startswith(b"ASRCTF{") and candidate.endswith(b"}"):
            print(candidate.decode())
            return
    print("Flag not found.")


if __name__ == "__main__":
    main()
