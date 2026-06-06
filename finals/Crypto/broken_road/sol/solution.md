Broken Road - Solution

Both signatures share the same r value, which means they were produced with the same nonce k. Since each signature satisfies s = k⁻¹(z + rd) mod n, subtracting the two equations cancels d and gives k = (z1 - z2) · (s1 - s2)⁻¹ mod n. With k recovered, the private key follows immediately from either equation as d = (s1 · k - z1) · r⁻¹ mod n. The flag is then recovered by XOR-ing encrypted_flag against the first 39 bytes of SHA256(d) ‖ d.

```bash
pip install ecdsa
python3 solve.py
```

Flag: `ASRCTF{n0nc3_sh4ll_b3_th3_d34th_0f_y0u}`
