Commitment Issues - Solution

n = 1296001987165015643369032371289 is a Carmichael number (6000003067 * 12000006133 * 18000009199,
Chernick construction). It passes Fermat primality tests but is composite, so lambda(n) =
lcm(p1-1, p2-1, p3-1) = 36000018396, not n-1. The group order factors smoothly (largest
prime 528821), so Pohlig-Hellman recovers x_eff = log_g(h) mod lambda(n) = 23104835483 via
BSGS in each prime subgroup, combined with generalised CRT. With x_eff, equivocating any
commitment is trivial: r2 = (x_eff*r1 - 1) * x_eff^-1 mod lambda(n).

```bash
python3 solve.py
```

Flag: ASRCTF{pr1m35_4r3_qu1t3_1ntr1gu1ng}
