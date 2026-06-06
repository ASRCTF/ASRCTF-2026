Dead Star - Solution

Two ciphertexts, one modulus. Both encrypted with standard-looking exponents (65537 and 65539) against the same n.

The attack works because gcd(e1, e2) = 1, so by Bézout's identity there exist integers a, b such that a·e1 + b·e2 = 1. Extended Euclidean gives a = 32769, b = −32768. Then:

    c1^a · c2^b ≡ m^(a·e1 + b·e2) ≡ m^1 (mod n)

The negative exponent is handled as a modular inverse: c2^(−|b|) becomes pow(c2, |b|, n)^(−1) mod n.

```bash
python3 solve.py
```

Flag: `ASRCTF{s4m3_n_tw1c3_1s_n0t_n1c3}`
