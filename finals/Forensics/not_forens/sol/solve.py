import re
import struct
import sys
from pathlib import Path

try:
    from scapy.all import rdpcap
    from scapy.layers.dns import DNS, DNSQR
except ImportError:
    sys.exit("pip install scapy")

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as crypto_padding
except ImportError:
    sys.exit("pip install cryptography")

DIST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist"


def solve_layer1() -> str:
    packets = rdpcap(str(DIST / "capture_47.pcap"))
    pattern = re.compile(r"^([0-9a-f]{2,4})\.seq(\d{2})\.sync\.corp-fileserver\.internal\.$", re.I)
    found: dict[int, str] = {}
    for pkt in packets:
        if not pkt.haslayer(DNS):
            continue
        dns = pkt[DNS]
        if dns.qr != 0 or not dns.qd:
            continue
        m = pattern.match(dns.qd.qname.decode(errors="ignore"))
        if m:
            found[int(m.group(2))] = m.group(1)
    if not found:
        sys.exit("layer 1: no covert queries found")
    filename = bytes.fromhex("".join(v for _, v in sorted(found.items()))).decode()
    print(f"[1] {filename}")
    return filename


def solve_layer2(db_filename: str) -> tuple[str, str]:
    raw = (DIST / db_filename).read_bytes()
    m = re.search(rb"key=([0-9a-f]{32})\s+next=([\w.]+)", raw)
    if not m:
        sys.exit(f"layer 2: pattern not found in {db_filename}")
    aes_key, next_file = m.group(1).decode(), m.group(2).decode()
    print(f"[2] key={aes_key}  next={next_file}")
    return aes_key, next_file


def solve_layer3(dd_filename: str, aes_key_hex: str) -> tuple[int, str]:
    BLOCK_SIZE = 1024
    INODE_SIZE = 128
    data = (DIST / dd_filename).read_bytes()
    iv, ct = data[:16], data[16:]
    dec    = Cipher(algorithms.AES(bytes.fromhex(aes_key_hex)), modes.CBC(iv)).decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = crypto_padding.PKCS7(128).unpadder()
    image  = unpadder.update(padded) + unpadder.finalize()
    if image[BLOCK_SIZE + 56: BLOCK_SIZE + 58] != b"\x53\xef":
        sys.exit("layer 3: bad ext2 magic after decrypt")
    bg_inode_tbl = struct.unpack_from("<I", image, 2 * BLOCK_SIZE + 8)[0]
    inode_tbl_off = bg_inode_tbl * BLOCK_SIZE
    for i in range(16):
        off = inode_tbl_off + i * INODE_SIZE
        i_mode   = struct.unpack_from("<H", image, off)[0]
        i_size   = struct.unpack_from("<I", image, off + 4)[0]
        i_block0 = struct.unpack_from("<I", image, off + 40)[0]
        if (i_mode & 0o170000) == 0o100000 and 0 < i_size < 100 and i_block0 > 0:
            slack = image[i_block0 * BLOCK_SIZE + i_size: (i_block0 + 1) * BLOCK_SIZE]
            if b"xor_key=" in slack:
                m = re.search(rb"xor_key=([0-9A-Fa-f]{8})\s+next=([\w.]+)", slack)
                if m:
                    xor_key, next_file = int(m.group(1), 16), m.group(2).decode()
                    print(f"[3] xor_key=0x{xor_key:08X}  next={next_file}")
                    return xor_key, next_file
    sys.exit("layer 3: slack secret not found")


def solve_layer4(core_filename: str, xor_key: int) -> str:
    raw = (DIST / core_filename).read_bytes()
    assert raw[:4] == b"\x7fELF"
    e_phoff = struct.unpack_from("<Q", raw, 32)[0]
    e_phnum = struct.unpack_from("<H", raw, 56)[0]
    note_off = note_sz = 0
    loads: list[tuple[int, int, int]] = []
    for i in range(e_phnum):
        ph = e_phoff + i * 56
        p_type   = struct.unpack_from("<I", raw, ph)[0]
        p_offset = struct.unpack_from("<Q", raw, ph + 8)[0]
        p_vaddr  = struct.unpack_from("<Q", raw, ph + 16)[0]
        p_filesz = struct.unpack_from("<Q", raw, ph + 32)[0]
        if p_type == 4:
            note_off, note_sz = p_offset, p_filesz
        elif p_type == 1:
            loads.append((p_vaddr, p_offset, p_filesz))
    target_vaddr = None
    pos = note_off
    while pos < note_off + note_sz:
        namesz = struct.unpack_from("<I", raw, pos)[0]
        descsz = struct.unpack_from("<I", raw, pos + 4)[0]
        ntype  = struct.unpack_from("<I", raw, pos + 8)[0]
        name_end = pos + 12 + ((namesz + 3) & ~3)
        desc = raw[name_end: name_end + descsz]
        if ntype == 0x46494c45 and len(desc) > 16:
            count = struct.unpack_from("<Q", desc, 0)[0]
            names = desc[16 + count * 24:].split(b"\x00")
            for j, fname in enumerate(names):
                if fname == b"[dead_drop_payload]":
                    target_vaddr = struct.unpack_from("<Q", desc, 16 + j * 24)[0]
                    break
        pos = name_end + ((descsz + 3) & ~3)
    if target_vaddr is None:
        sys.exit("layer 4: NT_FILE entry not found")
    for vaddr, offset, filesz in loads:
        if vaddr == target_vaddr:
            key_bytes = struct.pack(">I", xor_key)
            flag = bytes(b ^ key_bytes[i % 4] for i, b in enumerate(raw[offset: offset + filesz]))
            return flag.rstrip(b"\x00").decode()
    sys.exit(f"layer 4: no PT_LOAD at vaddr 0x{target_vaddr:X}")


def main():
    db   = solve_layer1()
    key, dd = solve_layer2(db)
    xor, core = solve_layer3(dd, key)
    flag = solve_layer4(core, xor)
    print(f"Flag: {flag}")


if __name__ == "__main__":
    main()
