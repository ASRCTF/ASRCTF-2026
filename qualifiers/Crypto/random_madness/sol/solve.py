from randcrack import RandCrack
from Crypto.Util.number import long_to_bytes
from sympy import nextprime
import re

with open("dist.txt") as f:
    data = f.read()

leak_line = re.search(r"leak = \((.*)\)\n", data).group(1)
n = int(re.search(r"n = (\d+)", data).group(1))
enc = int(re.search(r"enc = (\d+)", data).group(1))

cipher_str, plaintext = eval("(" + leak_line + ")")

cipher = cipher_str.split("0x")[1:]
cipher = [int(x, 16) for x in cipher]

rc = RandCrack()

for i in range(624):
    rng_val = cipher[i] ^ ord(plaintext[i])
    rc.submit(rng_val)

print("[+] MT state recovered")

def recover_prime():
    val = rc.predict_getrandbits(32)
    big = int(str(val) * 10)
    return nextprime(big)

p = recover_prime()
q = recover_prime()

print(f"[+] p = {p}")
print(f"[+] q = {q}")

phi = (p - 1) * (q - 1)
e = 65537
d = pow(e, -1, phi)

flag = long_to_bytes(pow(enc, d, n))
print(f"[+] FLAG: {flag}")