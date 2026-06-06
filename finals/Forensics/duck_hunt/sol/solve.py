import base64
import struct
import sys
from pathlib import Path


DISK        = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist" / "yata_disk.img"
SECTOR      = 512
PDF_SIG     = b"%PDF-"
RESERVED    = 1
FAT_SECTORS = 9
ROOT_ENTRIES= 224
ROOT_SECTORS= (ROOT_ENTRIES * 32 + SECTOR - 1) // SECTOR
DATA_START  = RESERVED + 2 * FAT_SECTORS + ROOT_SECTORS
ROOT_OFF    = (RESERVED + 2 * FAT_SECTORS) * SECTOR


def carve(raw: bytes) -> bytes:
    for i in range(ROOT_ENTRIES):
        e = raw[ROOT_OFF + i*32 : ROOT_OFF + i*32 + 32]
        if e[0] == 0x00:
            break
        if e[0] != 0xE5 or e[8:11].strip() != b"PDF":
            continue
        cluster = struct.unpack_from("<H", e, 26)[0]
        size    = struct.unpack_from("<I", e, 28)[0]
        offset  = (DATA_START + (cluster - 2)) * SECTOR
        return raw[offset : offset + size]

    pos = raw.find(PDF_SIG)     
    end = raw.find(b"%%EOF", pos) + len(b"%%EOF\n")
    return raw[pos:end]


def caesar(s: str, n: int) -> str:
    out = []
    for c in s:
        if c.isalpha():
            base = ord("a") if c.islower() else ord("A")
            out.append(chr((ord(c) - base + n) % 26 + base))
        else:
            out.append(c)
    return "".join(out)


def decode(pdf: bytes) -> str:
    b64_payload = b""
    key_shifted = ""

    for line in pdf.split(b"\n"):
        if line.startswith(b"%% DRAFT-REF: "):
            b64_payload = line[len(b"%% DRAFT-REF: "):] 
        if line.startswith(b"%% INT-KEY: "):
            key_shifted = line[len(b"%% INT-KEY: "):].decode()  

    key_hex = caesar(key_shifted, -7)                  
    key     = int(key_hex, 16)       
    xored   = base64.b64decode(b64_payload)
    return "".join(chr(b ^ key) for b in xored)        


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(DISK)
    pdf  = carve(Path(path).read_bytes())
    Path("PLAN_carved.pdf").write_bytes(pdf)
    flag = decode(pdf)
    print(f"Flag: {flag}")
