import sys
from pathlib import Path

ROUND_KEYS = [0xB5A4, 0x6C3D, 0xF1E2]
ROUNDS     = 3
BLOCK_SIZE = 4
NUM_BLOCKS = 9
TARGET_LEN = BLOCK_SIZE * NUM_BLOCKS


def decrypt_block(block, block_idx):
    L = int.from_bytes(block[:2], "little")
    R = int.from_bytes(block[2:], "little")
    for r in reversed(range(ROUNDS)):
        key = (ROUND_KEYS[r] ^ (block_idx * 0x5A)) & 0xFFFF
        F   = ((L * key) ^ (L >> 1)) & 0xFFFF
        L, R = (R ^ F) & 0xFFFF, L
    return L.to_bytes(2, "little") + R.to_bytes(2, "little")


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
    binary = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("crackme")
    rodata = extract_rodata(binary)
    for start in range(len(rodata) - TARGET_LEN + 1):
        chunk = rodata[start: start + TARGET_LEN]
        plaintext = b"".join(
            decrypt_block(chunk[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE], i)
            for i in range(NUM_BLOCKS)
        )
        if plaintext.startswith(b"ASRCTF{") and plaintext.endswith(b"}"):
            print(plaintext.decode())
            return


if __name__ == "__main__":
    main()
