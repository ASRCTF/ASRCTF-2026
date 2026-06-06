#!/usr/bin/env python3

from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import getPrime, isPrime
import random
import os

FLAG = b"ASRCTF{congrats_you_solved_the_easiest_challenge}"

def gen_params(q_bits=160, k_bits=256):
    while True:
        q = getPrime(q_bits)
        while True:
            k = random.getrandbits(k_bits)
            if k < 2:
                continue
            p = k * q + 1
            if isPrime(p):
                break

        while True:
            h = random.randrange(2, p - 1)
            g = pow(h, (p - 1) // q, p)
            if g != 1:
                return p, q, g

p, q, g = gen_params()

x = random.randrange(1, q)
y = pow(g, x, p)

B = 24
NUM_SIGS = 26

records = []
while len(records) < NUM_SIGS:
    msg = f"msg_{len(records)}".encode()
    h = int.from_bytes(sha256(msg).digest(), "big") % q

    a = random.randrange(1, q >> B)
    e = random.randrange(-(1 << (B - 1)), (1 << (B - 1)))
    k = ((a << B) + e) % q
    if k == 0:
        continue

    r = pow(g, k, p) % q
    if r == 0:
        continue

    s = (pow(k, -1, q) * (h + x * r)) % q
    if s == 0:
        continue

    records.append((msg.decode(), h, r, s, a))

key = sha256(str(x).encode()).digest()
iv = os.urandom(16)
ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(FLAG, 16))

with open("output.txt", "w") as f:
    f.write(f"p = {p}\n")
    f.write(f"q = {q}\n")
    f.write(f"g = {g}\n")
    f.write(f"y = {y}\n")
    f.write(f"B = {B}\n")
    f.write(f"records = {records}\n")
    f.write(f"iv = {iv.hex()}\n")
    f.write(f"ct = {ct.hex()}\n")

print("written to output.txt")