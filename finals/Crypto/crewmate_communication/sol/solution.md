crewmate_communication — Solution

Two files: a BB84 key exchange transcript for each of the seven crew members, and a set of Shamir shares. Two channels were intercepted; the corresponding shares are poisoned. Find the bad channels, drop their shares, recover the secret.

In bb84_transcripts.json, each entry has alice_sifted_bits and bob_sifted_bits for the positions where they chose the same basis. On a clean channel these match exactly. Interception forces Eve to guess bases, flipping ~25% of sifted bits. Compute the error rate per crew member — two stand out:

| Crew | Errors / Sifted | Rate |
|------|-----------------|------|
| 1 | 0 / 17 | 0% |
| 2 | 0 / 21 | 0% |
| **3** | **5 / 25** | **20%** |
| 4 | 0 / 25 | 0% |
| 5 | 0 / 20 | 0% |
| **6** | **4 / 19** | **21%** |
| 7 | 0 / 16 | 0% |

Discard crew 3 and 6.

`shares.txt` is a (n=7, k=5) Shamir scheme over GF(2⁵²¹−1). Five honest shares suffice. Apply Lagrange interpolation to crews 1, 2, 4, 5, 7 and decode the constant term as big-endian UTF-8.

```
python3 solve.py
```

Flag: `ASRCTF{th4t5_4_l0t_0f_j4rg0n}`
