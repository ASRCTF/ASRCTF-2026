not_my_type - Solution

The flag is verified inside a stripped ELF binary through a length check
followed by an XOR-keystream comparison against a hard-coded byte table in
.rodata. Decompiling main() reveals the input must be exactly 28 bytes, after
which each character is XORed with a keystream byte derived from a 32-bit LCG
seeded with 0xDEADC0DE, using the Numerical Recipes multiplier (1664525) and
addend (1013904223). The key byte at each position is (state >> 16) & 0xFF.
Replaying the LCG and XORing against the 28 encrypted bytes in .rodata recovers
the flag directly.

```bash
python3 solve.py crackme
```

Flag: ASRCTF{r4nd0m1s3r_ch1c4n3ry}
