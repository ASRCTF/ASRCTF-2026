import struct, hashlib
from elftools.elf.elffile import ELFFile
from pathlib import Path

elf_path = Path(__file__).parent.parent / "dist" / "firmware.elf"

with open(elf_path, "rb") as f:
    elf = ELFFile(f)

    comment_sec = elf.get_section_by_name(".comment")
    data = comment_sec.data()
    pos = 0
    entries = []
    while pos < len(data):
        off, flag, name_len = struct.unpack_from("<IBB", data, pos)
        pos += 6
        name = data[pos:pos + name_len]
        pos += name_len
        if flag == 0x01:
            entries.append((off, name.decode()))

    entries.sort(key=lambda x: x[0])

    note_sec = elf.get_section_by_name(".note.build")
    note_data = note_sec.data()
    namesz, descsz, _ = struct.unpack_from("<III", note_data)
    nb_name = note_data[12:12 + namesz].rstrip(b'\x00')
    nb_desc = note_data[12 + namesz:12 + namesz + descsz].rstrip(b'\x00')
    build_time = nb_desc

    key = hashlib.md5(build_time).digest()

    rodata_sec = elf.get_section_by_name(".rodata")
    rodata = rodata_sec.data()

pdf_bytes = bytes(b ^ key[i % len(key)] for i, b in enumerate(rodata))

out = Path(__file__).parent / "recovered.pdf"
out.write_bytes(pdf_bytes)
print(f"Recovered PDF written to {out}")
