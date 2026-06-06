import os
import struct
import time
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

OUT       = Path(__file__).parent.parent / "dist" / "fs_shard.dd"
AES_KEY   = bytes.fromhex("b7e3a914c6f82d053f9a1b7c4e8d2f60")
XOR_KEY   = 0xCAFED00D
NEXT_FILE = "coredump.bin"

BLOCK_SIZE       = 1024
NUM_BLOCKS       = 128
INODE_SIZE       = 128
INODES_PER_GROUP = 16

INO_README   = 11
INO_OPS_DIR  = 12
INO_TRANSFER = 13
INO_CHECKS   = 14
INO_ARCHIVE  = 15

BLK_SUPERBLOCK   = 1
BLK_GDT          = 2
BLK_BLOCK_BITMAP = 3
BLK_INODE_BITMAP = 4
BLK_INODE_TABLE  = 5
BLK_ROOT_DIR     = 8
BLK_README       = 9
BLK_OPS_DIR      = 10
BLK_TRANSFER     = 11
BLK_CHECKS       = 12
BLK_ARCHIVE_DIR  = 13


def pad_block(data: bytes, size: int = BLOCK_SIZE) -> bytes:
    return data + b"\x00" * (size - len(data))


def make_superblock() -> bytes:
    sb = bytearray(1024)
    struct.pack_into("<I", sb,  0, INODES_PER_GROUP)
    struct.pack_into("<I", sb,  4, NUM_BLOCKS)
    struct.pack_into("<I", sb,  8, 5)
    struct.pack_into("<I", sb, 12, NUM_BLOCKS - BLK_ARCHIVE_DIR - 1)
    struct.pack_into("<I", sb, 16, INODES_PER_GROUP - 6)
    struct.pack_into("<I", sb, 20, 1)
    struct.pack_into("<I", sb, 24, 0)
    struct.pack_into("<I", sb, 28, 0)
    struct.pack_into("<I", sb, 32, NUM_BLOCKS)
    struct.pack_into("<I", sb, 36, NUM_BLOCKS)
    struct.pack_into("<I", sb, 40, INODES_PER_GROUP)
    struct.pack_into("<I", sb, 44, int(time.time()) - 3600)
    struct.pack_into("<I", sb, 48, int(time.time()))
    struct.pack_into("<H", sb, 52, 1)
    struct.pack_into("<H", sb, 54, 20)
    struct.pack_into("<H", sb, 56, 0xEF53)
    struct.pack_into("<H", sb, 58, 1)
    struct.pack_into("<H", sb, 60, 1)
    struct.pack_into("<I", sb, 76, 0)
    struct.pack_into("<I", sb, 84, 11)
    struct.pack_into("<H", sb, 88, INODE_SIZE)
    sb[120:136] = b"NOT_FORENS_FS\x00\x00\x00"
    return bytes(sb)


def make_gdt() -> bytes:
    gdt = bytearray(BLOCK_SIZE)
    struct.pack_into("<I", gdt,  0, BLK_BLOCK_BITMAP)
    struct.pack_into("<I", gdt,  4, BLK_INODE_BITMAP)
    struct.pack_into("<I", gdt,  8, BLK_INODE_TABLE)
    struct.pack_into("<H", gdt, 12, NUM_BLOCKS - BLK_ARCHIVE_DIR - 1)
    struct.pack_into("<H", gdt, 14, INODES_PER_GROUP - 6)
    struct.pack_into("<H", gdt, 16, 3)
    return bytes(gdt)


def make_block_bitmap() -> bytes:
    bm = bytearray(BLOCK_SIZE)
    for blk in [BLK_SUPERBLOCK, BLK_GDT, BLK_BLOCK_BITMAP, BLK_INODE_BITMAP,
                BLK_INODE_TABLE, BLK_INODE_TABLE + 1,
                BLK_ROOT_DIR, BLK_README, BLK_OPS_DIR,
                BLK_TRANSFER, BLK_CHECKS, BLK_ARCHIVE_DIR]:
        bm[blk // 8] |= 1 << (blk % 8)
    return bytes(bm)


def make_inode_bitmap() -> bytes:
    bm = bytearray(BLOCK_SIZE)
    for ino in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                INO_README, INO_OPS_DIR, INO_TRANSFER, INO_CHECKS, INO_ARCHIVE]:
        idx = ino - 1
        bm[idx // 8] |= 1 << (idx % 8)
    return bytes(bm)


def make_inode(mode: int, size: int, blocks: list[int],
               uid: int = 1000, gid: int = 1000) -> bytes:
    inode = bytearray(INODE_SIZE)
    ts = int(time.time()) - 7200
    struct.pack_into("<H", inode,  0, mode)
    struct.pack_into("<H", inode,  2, uid)
    struct.pack_into("<I", inode,  4, size)
    struct.pack_into("<I", inode,  8, ts)
    struct.pack_into("<I", inode, 12, ts)
    struct.pack_into("<I", inode, 16, ts)
    struct.pack_into("<H", inode, 26, gid)
    struct.pack_into("<I", inode, 28, 2 * len(blocks))
    for i, blk in enumerate(blocks[:12]):
        struct.pack_into("<I", inode, 40 + i * 4, blk)
    return bytes(inode)


def make_inode_table(inodes: dict[int, bytes]) -> bytes:
    table = bytearray(BLOCK_SIZE * 2)
    for ino, data in inodes.items():
        offset = (ino - 1) * INODE_SIZE
        table[offset:offset + INODE_SIZE] = data
    return bytes(table)


def make_dir_block(entries: list[tuple[int, int, str]]) -> bytes:
    block = bytearray(BLOCK_SIZE)
    pos = 0
    for i, (ino, ftype, name) in enumerate(entries):
        raw_name = name.encode()
        rec_len  = (8 + len(raw_name) + 3) & ~3
        if i == len(entries) - 1:
            rec_len = BLOCK_SIZE - pos
        struct.pack_into("<I", block, pos,     ino)
        struct.pack_into("<H", block, pos + 4, rec_len)
        struct.pack_into("<B", block, pos + 6, len(raw_name))
        struct.pack_into("<B", block, pos + 7, ftype)
        block[pos + 8: pos + 8 + len(raw_name)] = raw_name
        pos += rec_len
    return bytes(block)


def make_transfer_block() -> bytes:
    visible = b"Operational log truncated. See archive.\n"
    secret  = f"xor_key={XOR_KEY:08X} next={NEXT_FILE}".encode()
    block   = bytearray(BLOCK_SIZE)
    block[:len(visible)] = visible
    block[len(visible): len(visible) + len(secret)] = secret
    return bytes(block)


def build_ext2_image() -> bytes:
    image = bytearray(NUM_BLOCKS * BLOCK_SIZE)

    def wb(blk, data):
        image[blk * BLOCK_SIZE: blk * BLOCK_SIZE + len(data)] = data

    wb(BLK_SUPERBLOCK,   make_superblock())
    wb(BLK_GDT,          make_gdt())
    wb(BLK_BLOCK_BITMAP, make_block_bitmap())
    wb(BLK_INODE_BITMAP, make_inode_bitmap())

    readme_content = (
        b"Operational transfer log archive.\n"
        b"See /ops/ for transfer records.\n"
        b"This volume is read-only after archival.\n"
    )
    checksums_content = (
        b"# SHA-256 checksums - generated by archival daemon\n"
        b"3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b  schedule_q1.tar.gz\n"
        b"f4a1c9b77d4c5d8e0f2a3b6c9e1d7f0a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4  manifest_march.json\n"
        b"1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b  ops_delta_0309.bin\n"
    )

    wb(BLK_ROOT_DIR, make_dir_block([
        (2,           2, "."), (2, 2, ".."),
        (INO_README,  1, "README.txt"), (INO_OPS_DIR, 2, "ops"),
    ]))
    wb(BLK_README, pad_block(readme_content))
    wb(BLK_OPS_DIR, make_dir_block([
        (INO_OPS_DIR,  2, "."), (2, 2, ".."),
        (INO_TRANSFER, 1, "transfer_log.txt"),
        (INO_CHECKS,   1, "checksums.txt"),
        (INO_ARCHIVE,  2, "archive"),
    ]))
    wb(BLK_TRANSFER, make_transfer_block())
    wb(BLK_CHECKS, pad_block(checksums_content))
    wb(BLK_ARCHIVE_DIR, make_dir_block([(INO_ARCHIVE, 2, "."), (INO_OPS_DIR, 2, "..")]))

    REG = 0o100644
    DIR = 0o040755
    wb(BLK_INODE_TABLE, make_inode_table({
        2:            make_inode(DIR, BLOCK_SIZE,             [BLK_ROOT_DIR]),
        INO_README:   make_inode(REG, len(readme_content),    [BLK_README]),
        INO_OPS_DIR:  make_inode(DIR, BLOCK_SIZE,             [BLK_OPS_DIR]),
        INO_TRANSFER: make_inode(REG, 40,                     [BLK_TRANSFER]),
        INO_CHECKS:   make_inode(REG, len(checksums_content), [BLK_CHECKS]),
        INO_ARCHIVE:  make_inode(DIR, BLOCK_SIZE,             [BLK_ARCHIVE_DIR]),
    }))

    return bytes(image)


def _aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    padder = crypto_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return enc.update(padded) + enc.finalize()


def _aes_cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = dec.update(ciphertext) + dec.finalize()
    unpadder = crypto_padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def build():
    plaintext  = build_ext2_image()
    iv         = os.urandom(16)
    ciphertext = _aes_cbc_encrypt(AES_KEY, iv, plaintext)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(iv + ciphertext)

    recovered   = _aes_cbc_decrypt(AES_KEY, iv, ciphertext)
    slack_start = BLK_TRANSFER * BLOCK_SIZE + 40
    slack_bytes = recovered[slack_start: slack_start + 40]
    assert b"CAFED00D" in slack_bytes
    assert b"coredump.bin" in slack_bytes


if __name__ == "__main__":
    build()
