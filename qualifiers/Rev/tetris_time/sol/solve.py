import sys
from pathlib import Path

# Galois 16-bit LFSR: seed 0xACE1, tap mask 0xB400
LFSR_SEED = 0xACE1
LFSR_TAP  = 0xB400
FLAG_LEN  = 29


def lfsr_stream(length):
    reg = LFSR_SEED
    stream = []
    for _ in range(length):
        byte = 0
        for b in range(8):
            lsb = reg & 1
            reg = (reg >> 1) ^ (LFSR_TAP if lsb else 0)
            byte = (byte >> 1) | (lsb << 7)
        stream.append(byte & 0xFF)
    return stream


def extract_rodata(path):
    raw = path.read_bytes()
    e_shoff     = int.from_bytes(raw[0x28:0x30], "little")
    e_shentsize = int.from_bytes(raw[0x3A:0x3C], "little")
    e_shnum     = int.from_bytes(raw[0x3C:0x3E], "little")
    e_shstrndx  = int.from_bytes(raw[0x3E:0x40], "little")
    str_hdr     = e_shoff + e_shstrndx * e_shentsize
    str_off     = int.from_bytes(raw[str_hdr + 0x18:str_hdr + 0x20], "little")
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
    binary = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tetris_time")
    rodata = extract_rodata(binary)
    stream = lfsr_stream(FLAG_LEN)
    for start in range(len(rodata) - FLAG_LEN + 1):
        candidate = bytes(rodata[start + i] ^ stream[i] for i in range(FLAG_LEN))
        if candidate.startswith(b"ASRCTF{") and candidate.endswith(b"}"):
            print(candidate.decode())
            return
    print("Flag not found.")


if __name__ == "__main__":
    main()
