🐴🐴🐴🐴🐴 - Solution

The dispatch encodes the ciphertext as 🐴/🐎 emoji pairs: 8 per byte, MSB first,
space-delimited, where 🐴 is 1 and 🐎 is 0. Decoding each group as a binary integer
recovers the ASCII ciphertext.

That ciphertext is the result of a columnar transposition keyed on the reference race
results. The five horses' finishing positions in post order (3,1,5,2,4) give the column
read order during encryption: finish rank 1st→2nd→3rd→4th→5th maps to column indices
[1,3,0,4,2]. Inverting the transposition (40 chars, 5 columns of 8 rows) recovers the
Vigenère intermediate, trimming the trailing ~ pad.

The Vigenère key is SHADOWMERE (the scratched stable favourite listed in the dispatch).
The cipher runs over the full printable ASCII range (codes 32–126, modulus 95).

```bash
python3 solve.py
```

Flag: ASRCTF{w3_d0_4_b1t_0f_h0r51ng_4r0und}
