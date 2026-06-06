import random
import string
from sympy import nextprime
from Crypto.Util.number import bytes_to_long

FLAG = b"ASRCTF{REDACTED}"

random.seed(REDACTED)

def gen_prime():
    return nextprime(int(str(random.getrandbits(32))*10))

def generate_leak(leak):
    plaintext = [random.choice(string.ascii_letters) for _ in range(624)]
    cipher = []
    for i in range(624):
        cipher.append(hex(ord(plaintext[i]) ^ leak[i]))
    return ("".join(cipher), "".join(plaintext))

rng = [random.getrandbits(32) for _ in range(624)]

p = gen_prime()
q = gen_prime()
n = p * q
e = 65537

enc = pow(bytes_to_long(FLAG), e, n)

with open("dist.txt", "w") as file:
    file.write(str("leak = " + str(generate_leak(rng)) + "\n"))
    file.write(str("n = " + str(n) + "\n"))
    file.write(str("enc = " + str(enc) + "\n"))