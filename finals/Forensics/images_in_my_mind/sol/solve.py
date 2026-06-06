import struct
import re
import base64
import zlib
from pathlib import Path

ROOT = Path(__file__).parent.parent / "dist"

def extract_msd_payload(path):
    data = path.read_bytes()
    chunks = []
    i = 0
    while i < len(data):
        if i + 8 > len(data):
            break
        block_type = struct.unpack_from("<I", data, i)[0]
        block_len  = struct.unpack_from("<I", data, i+4)[0]
        if block_len < 12 or i + block_len > len(data):
            break
        if block_type == 6:
            body = data[i+8:i+block_len-4]
            pkt  = body[20:]
            if pkt[:2] == b"\xf0\x00":
                chunks.append(pkt[2:])
        i += block_len
    return b"".join(chunks)

def parse_png_text(png_bytes):
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    fields = {}
    pos = 8
    while pos < len(png_bytes):
        length = struct.unpack_from(">I", png_bytes, pos)[0]
        tag    = png_bytes[pos+4:pos+8]
        data   = png_bytes[pos+8:pos+8+length]
        if tag == b"tEXt":
            sep = data.index(b"\x00")
            fields[data[:sep].decode()] = data[sep+1:]
        pos += 12 + length
    return fields

def extract_etcd_fragment(path):
    data  = path.read_bytes()
    match = re.search(rb"/registry/secrets/[^\x00]+(.+?)(?=\x00\x00|\Z)", data, re.DOTALL)
    if not match:
        raise ValueError("secret key not found in snapshot")
    yaml_blob = match.group(1)
    m = re.search(rb"fragment:\s+([A-Za-z0-9+/=]+)", yaml_blob)
    if not m:
        raise ValueError("fragment field not found")
    return base64.b64decode(m.group(1))

png_bytes = extract_msd_payload(ROOT / "capture.pcapng")
text_fields = parse_png_text(png_bytes)
part1 = text_fields["fragment"]

part2 = extract_etcd_fragment(ROOT / "etcd.snapshot")

print((part1 + part2).decode())
