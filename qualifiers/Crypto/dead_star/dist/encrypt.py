from sympy import randprime
from secret import flag

p = randprime(2**511, 2**512)
q = randprime(2**511, 2**512)
n = p * q

e1 = 65537
e2 = 65539

m = int.from_bytes(flag, "big")
c1 = pow(m, e1, n)
c2 = pow(m, e2, n)

print(f"n  = {n}")
print(f"e1 = {e1}")
print(f"e2 = {e2}")
print(f"c1 = {c1}")
print(f"c2 = {c2}")
