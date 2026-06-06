import os
import random


flag = b"ASRCTF{???}"
LENGTH = len(flag)
keys = [os.urandom(LENGTH) for _ in range(676767)]

def xor(pt, key):
    return bytes([p ^ k for p, k in zip(pt, key)])


ct = flag
for key in keys:
    ct = xor(ct, key)

random.shuffle(keys)
with open("keys.txt", "wb") as file:
    for key in keys:
        file.write(key)

with open("ciphertext.txt", "wb") as file:
    file.write(ct)
