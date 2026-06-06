Talking Firmware - Solution

Part 1: The .comment section encodes 12 pseudo-DWARF entries, each prefixed with an offset and a validity flag byte. Filtering for flag == 0x01 and sorting by offset yields four names: xor_block, rodata_seg, md5_derive, note_build_ts, the instruction to XOR .rodata with MD5(.note.build). The .note.build section contains the timestamp 2031-05-14T08:42:00Z. Deriving the key and XOR-ing .rodata recovers a PDF.

Part 2: The PDF carries a hidden FontDescriptor object attached to page resources under an inconspicuous font alias. Its /Notice field holds the flag.

```bash
pip install pyelftools pikepdf reportlab
python3 solve_part1.py
python3 solve_part2.py
```

Flag: ASRCTF{z3r0_c0rr3l4t10n_wh4ts03v3r}
