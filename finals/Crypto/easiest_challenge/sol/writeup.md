# easiest_challenge

## Challenge Overview

`chall.py` is heavily obfuscated, but after peeling the layers its a simple DSA-like signing script plus AES-CBC encryption.

## Analysis

> FOR PARTICIPANTS:
> 
> the files starting with 0 are unencrypted, files starting with 1 are obfuscated with PyObfuscator, files starting with 2 are obfuscated fully. UNREDACTED and REDACTED specifies whether the flag is redacted in that specific file
>
> for those who are curious, the file was encrypted the following way: original code -> PyObfuscator -> further obfuscated with [pyobfusinator](https://dthung1602.github.io/pyobfusinator/) "compress" -> code provided to participants

the first step is to undo the decryption (obviously). from the participants perspective, theres some unicode junk, a hex-escaped stub, base85, xor, as well as gzip

the relevant logic is as follows:

- generate DSA parameters `(p, q, g)` with subgroup order `q`
- choose priv key `x`, pub key `y = g^x mod p`.
- for each msg:
  - hash the message to `h`
  - build a nonce as `k = ((a << 24) + b) mod q`
  - output `(msg_name, h, r, s, a)`
- derive the AES key as `sha256(str(x).encode()).digest()`
- encrypt the flag under AES-CBC

the important bug here is that each record leaks `a`, which is almost the whole nonce. only a small signed error `b` remains unknown. this makes the challenge extremely easy, hence inspiring the challenge name

## Exploit

the signature eqn is standard:

`s = k^{-1} (h + x r) mod q`

rearrange it:

`x * (r * s^{-1}) - (a * 2^24 - h * s^{-1}) = b mod q`

define:

- `t = r * s^{-1} mod q`
- `u = a * 2^24 - h * s^{-1} mod q`

each transcript gives:

`x * t - u = b mod q`

where `b` is very small, roughly bounded by `2^23`

at this point, the challenge becomes simple. this is a clear hidden number problem. we build the usual lattice embedding from a small subset of signatures, run `LLL`, then read the correct solution from the unimodular transform returned by `sympy.Matrix(...).lll_transform()`. critically, the priv key is recovered from the transform coeffs, not directly from the reduced basis vector coordinates

private key:

`x = 718084012133266972330582699056263489020370742806`

then we simply `key = sha256(str(x).encode()).digest()`, decrypt `ct` with AES-CBC with the provided `iv` and unpad, which gives us the flag

> note for participants:
>
>- reading `x` directly from the reduced lattice basis vector produces the wrong candidate
>- using a Babai/CVP approach does not recover the key

## Full exploit code

### `exploit.py`

```python
#!/usr/bin/env python3
import ast
import hashlib
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sympy import Matrix


def parse_output(path: str):
    data = {}
    for line in Path(path).read_text().splitlines():
        key, value = line.split(" = ", 1)
        if key in {"p", "q", "g", "y", "B"}:
            data[key] = int(value)
        elif key == "records":
            data[key] = ast.literal_eval(value)
        elif key in {"iv", "ct"}:
            data[key] = bytes.fromhex(value)
    return data


def recover_x(data):
    q = data["q"]
    p = data["p"]
    g = data["g"]
    y = data["y"]
    bound_bits = data["B"]
    records = data["records"]
    leak_scale = 1 << bound_bits

    pairs = []
    for _, h, r, s, a in records[:6]:
        s_inv = pow(s, -1, q)
        t = (r * s_inv) % q
        u = (a * leak_scale - h * s_inv) % q
        pairs.append((t, u))

    q2 = q * q
    embed = 1 << 175
    rows = []
    for i in range(len(pairs)):
        row = [0] * (len(pairs) + 2)
        row[i] = q2
        rows.append(row)

    rows.append([q * t for t, _ in pairs] + [leak_scale, 0])
    rows.append([q * u for _, u in pairs] + [0, embed])

    _, transform = Matrix(rows).lll_transform()
    for i in range(transform.rows):
        coeffs = list(map(int, transform.row(i)))
        if abs(coeffs[-1]) != 1:
            continue
        x = (-coeffs[-2] * coeffs[-1]) % q
        if pow(g, x, p) == y:
            return x

    raise RuntimeError("failed to recover x")


def decrypt_flag(data, x: int) -> str:
    key = hashlib.sha256(str(x).encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, data["iv"])
    return unpad(cipher.decrypt(data["ct"]), 16).decode()


def main():
    data = parse_output("output.txt")
    x = recover_x(data)
    print(decrypt_flag(data, x))


if __name__ == "__main__":
    main()
```

## Flag

`ASRCTF{congrats_you_solved_the_easiest_challenge}`
