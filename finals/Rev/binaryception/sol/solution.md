Binaryception - Solution

The flag lives entirely inside a 1599-byte bytecode blob sitting in .rodata, which the dispatcher blindly executes.

The blob is structured as 38 identical 42-byte blocks followed by a three-byte RET. Each block handles one character of the 38-byte flag. Disassembling a single block reveals the pattern: read one input byte with GETC, XOR it against a position-derived key loaded by LOAD, apply an 8-bit left-rotation by 3 (constructed from a SHL 3 and SHR 5 pair whose results are XORed together since the bit ranges don't overlap for 8-bit inputs), mask to the low byte with AND 0xFF, then compare against a hard-coded expected byte. A JZ +3 skips over an inline FAIL on a match; a mismatch falls through to FAIL immediately.

The key for position i is (0x5F ^ (i * 0x07)) & 0xFF, readable directly from the second byte of each block's LOAD r1, key instruction at intra-block offset 5. The expected byte is at intra-block offset 32, the operand of LOAD r5, expected. Inverting the transform via rotr3(expected) ^ key recovers each plaintext character.

```bash
python3 solve.py binaryception
```

Flag: `ASRCTF{4_b1n4ry_1ns1d3_my_b1n4ry_wh4t}`
