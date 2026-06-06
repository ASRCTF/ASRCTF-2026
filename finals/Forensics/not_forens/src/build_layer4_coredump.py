import struct
from pathlib import Path

OUT     = Path(__file__).parent.parent / "dist" / "coredump.bin"
XOR_KEY = 0xCAFED00D
FLAG    = b"ASRCTF{50m3_m0r3_l3v3l5_w0uld_b3_n1ce}"


def xor_encode(data: bytes, key: int) -> bytes:
    kb = struct.pack(">I", key)
    return bytes(b ^ kb[i % 4] for i, b in enumerate(data))


def elf64_header(e_phoff: int, e_phnum: int) -> bytes:
    hdr = bytearray(64)
    hdr[0:4] = b"\x7fELF"
    hdr[4]   = 2
    hdr[5]   = 1
    hdr[6]   = 1
    struct.pack_into("<H", hdr, 16, 4)
    struct.pack_into("<H", hdr, 18, 0x3E)
    struct.pack_into("<I", hdr, 20, 1)
    struct.pack_into("<Q", hdr, 32, e_phoff)
    struct.pack_into("<H", hdr, 52, 64)
    struct.pack_into("<H", hdr, 54, 56)
    struct.pack_into("<H", hdr, 56, e_phnum)
    return bytes(hdr)


def elf64_phdr(p_type, p_flags, p_offset, p_vaddr, p_filesz, p_memsz, p_align=0x1000) -> bytes:
    ph = bytearray(56)
    struct.pack_into("<I", ph,  0, p_type)
    struct.pack_into("<I", ph,  4, p_flags)
    struct.pack_into("<Q", ph,  8, p_offset)
    struct.pack_into("<Q", ph, 16, p_vaddr)
    struct.pack_into("<Q", ph, 24, p_vaddr)
    struct.pack_into("<Q", ph, 32, p_filesz)
    struct.pack_into("<Q", ph, 40, p_memsz)
    struct.pack_into("<Q", ph, 48, p_align)
    return bytes(ph)


def note_entry(name: bytes, note_type: int, desc: bytes) -> bytes:
    def align4(b):
        return b + b"\x00" * ((4 - len(b) % 4) % 4)
    return struct.pack("<III", len(name) + 1, len(desc), note_type) + align4(name + b"\x00") + align4(desc)


def make_nt_prstatus(pid: int, comm: str) -> bytes:
    desc = bytearray(336)
    struct.pack_into("<I", desc,  0, 11)
    struct.pack_into("<I", desc, 24, pid)
    struct.pack_into("<I", desc, 28, 1)
    comm_b = comm.encode()[:15]
    desc[32:32 + len(comm_b)] = comm_b
    struct.pack_into("<Q", desc, 136 + 16 * 8, 0xDEAD0042)
    return bytes(desc)


def make_nt_file(mappings: list[tuple[int, int, int, str]]) -> bytes:
    header = struct.pack("<QQ", len(mappings), 0x1000)
    ranges = b"".join(struct.pack("<QQQ", s, e, o) for s, e, o, _ in mappings)
    names  = b"".join(n.encode() + b"\x00" for _, _, _, n in mappings)
    return header + ranges + names


def make_fake_text(size: int = 0x1000) -> bytes:
    buf = bytearray(size)
    for i in range(size):
        buf[i] = 0xC3 if i % 256 == 255 else (0x55 if i % 64 == 0 else 0x90)
    return bytes(buf)


def build():
    nt_prstatus = note_entry(b"CORE", 1, make_nt_prstatus(1337, "transfer_mgr"))
    nt_file     = note_entry(b"CORE", 0x46494c45, make_nt_file([
        (0x00400000, 0x00401000, 0, "/usr/bin/transfer_mgr"),
        (0x00600000, 0x00601000, 0, "/usr/bin/transfer_mgr"),
        (0x7FFD8000, 0x7FFF8000, 0, "[stack]"),
        (0xDEAD0000, 0xDEAD1000, 0, "[dead_drop_payload]"),
    ]))
    note_data    = nt_prstatus + nt_file
    text_data    = make_fake_text(0x1000)
    encoded_flag = xor_encode(FLAG + b"\x00" * (256 - len(FLAG)), XOR_KEY)

    E_PHOFF  = 64
    NOTE_OFF = E_PHOFF + 3 * 56
    NOTE_SZ  = len(note_data)
    TEXT_OFF = 0x1000
    FLAG_OFF = 0x2000

    phdrs = (
        elf64_phdr(4, 4, NOTE_OFF, 0,          NOTE_SZ,        NOTE_SZ,        4)
        + elf64_phdr(1, 5, TEXT_OFF, 0x00400000, len(text_data), len(text_data))
        + elf64_phdr(1, 6, FLAG_OFF, 0xDEAD0000, 256,            256)
    )

    core = bytearray(FLAG_OFF + 256)
    core[0:64]                          = elf64_header(E_PHOFF, 3)
    core[E_PHOFF: E_PHOFF + len(phdrs)] = phdrs
    core[NOTE_OFF: NOTE_OFF + NOTE_SZ]  = note_data
    core[TEXT_OFF: TEXT_OFF + 0x1000]   = text_data
    core[FLAG_OFF: FLAG_OFF + 256]      = encoded_flag

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(bytes(core))

    raw = OUT.read_bytes()
    assert raw[:4] == b"\x7fELF"
    assert xor_encode(raw[FLAG_OFF: FLAG_OFF + 256], XOR_KEY).rstrip(b"\x00") == FLAG


if __name__ == "__main__":
    build()
