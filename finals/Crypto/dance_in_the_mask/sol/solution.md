Dance in the Mask - Solution

The mask RNG is a 16-bit LCG,so only 2^16 possible seeds. Across 50k traces, birthday collisions are guaranteed. Fingerprint traces on their first 16 samples, find two that match, brute-force the seed. With all masks known, standard CPA recovers the key byte by byte.

```bash
pip install numpy
python3 solve.py
```

Flag: ASRCTF{ch4_ch4_r34l_sm00th}
