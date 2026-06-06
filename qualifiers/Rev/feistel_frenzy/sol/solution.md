feistel_frenzy - Solution

The binary encrypts the 36-byte input as nine consecutive 4-byte blocks using
a 3-round Feistel network and compares the result against a stored ciphertext
in .rodata. Each block is split into two 16-bit halves (L, R) in little-endian
order. In each round, a per-round key is derived by XORing one of three
hard-coded 16-bit constants (0xB5A4, 0x6C3D, 0xF1E2) with the block index
multiplied by 0x5A. The round function is F(R, key) = (R * key) ^ (R >> 1),
truncated to 16 bits. The swap is the standard Feistel swap: new L = R,
new R = L ^ F. After three rounds the two halves are written back
little-endian.

To recover the flag, reverse the Feistel: run the rounds in reverse order,
using L as the active half for F at each step (since after the forward swap,
what was R is now L), then set new R = L and new L = R ^ F.

```bash
python3 solve.py crackme
```

Flag: ASRCTF{f31st3l_m4k3s_1t_c0mpl1c4t3d}
