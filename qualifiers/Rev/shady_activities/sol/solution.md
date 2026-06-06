Shady Activities - Solution

The flag is hidden entirely inside a SPIR-V shader blob sitting in the binary's .rodata. There is no string comparison anywhere in the conventional sense — all the information needed to recover the flag lives in the shader's constant pool, and the binary exists mostly to walk that pool and write a PPM.

The first thing that jumps out on a hex dump is a 1616-byte region starting with 07 23 02 03 at file offset 0x2080. From there it's a matter of understanding just enough of the SPIR-V binary format to pull out what matters.

SPIR-V is a stream of 32-bit little-endian words. The first five form the module header; everything after is a sequence of instructions where the high 16 bits of the first word give the instruction length in words and the low 16 bits give the opcode. Opcode 0x2B is OpConstant, and each OpConstant instruction encodes a type ID, a result ID, and the literal value. Two banks of these stand out. Result IDs 12 through 51 are OpConstant float values with their literals, reinterpreted as IEEE 754 singles, land in the range [0, 1] and are clearly normalised byte values. Result IDs 52 through 91 are OpConstant int values in the range [0x42, 0xFC] with a gap, consistent with a linear sequence. Listing them in result-ID order immediately gives the key schedule: key[i] = (i * 31 + 0x42) & 0xFF.

The transform is: encoded[i] = flag[i] ^ key[i], stored as encoded[i] / 255.0 in the float constant. Inverting it is a one-liner: multiply the float back up to an integer and XOR against the corresponding key.

```bash
python3 solve.py shady_activities
```

Flag: ASRCTF{d1dnt_kn0w_sh4d3r5_c4n_b3_1n_r3v}
