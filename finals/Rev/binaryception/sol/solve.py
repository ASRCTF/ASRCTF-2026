import sys
from pathlib import Path

BINARY   = Path(__file__).parent.parent / "dist" / "binaryception"
FLAG_LEN = 38
BLOCK_SZ = 42


def read_rodata(path):
    raw = path.read_bytes()
    e_shoff     = int.from_bytes(raw[0x28:0x30], "little")
    e_shentsize = int.from_bytes(raw[0x3A:0x3C], "little")
    e_shnum     = int.from_bytes(raw[0x3C:0x3E], "little")
    e_shstrndx  = int.from_bytes(raw[0x3E:0x40], "little")
    strtab_hdr  = e_shoff + e_shstrndx * e_shentsize
    strtab_off  = int.from_bytes(raw[strtab_hdr + 0x18: strtab_hdr + 0x20], "little")
    for i in range(e_shnum):
        hdr  = e_shoff + i * e_shentsize
        noff = int.from_bytes(raw[hdr:hdr + 4], "little")
        name = raw[strtab_off + noff: strtab_off + noff + 16].split(b"\x00")[0]
        if name == b".rodata":
            off  = int.from_bytes(raw[hdr + 0x18: hdr + 0x20], "little")
            size = int.from_bytes(raw[hdr + 0x20: hdr + 0x28], "little")
            return raw[off: off + size]
    raise ValueError(".rodata not found")


def find_blob(rodata):
    for base in range(len(rodata) - BLOCK_SZ * 4):
        if all(rodata[base + j * BLOCK_SZ] == 0x0A and
               rodata[base + j * BLOCK_SZ + 3] == 0x01 and
               rodata[base + j * BLOCK_SZ + 4] == 0x01
               for j in range(4)):
            return base
    raise ValueError("bytecode blob not found")


def rotr3(v):
    return ((v >> 3) | (v << 5)) & 0xFF


def main():
    path   = Path(sys.argv[1]) if len(sys.argv) > 1 else BINARY
    rodata = read_rodata(path)
    base   = find_blob(rodata)
    flag   = bytes(
        rotr3(rodata[base + i * BLOCK_SZ + 32]) ^ rodata[base + i * BLOCK_SZ + 5]
        for i in range(FLAG_LEN)
    )
    print(flag.decode())


if __name__ == "__main__":
    main()
