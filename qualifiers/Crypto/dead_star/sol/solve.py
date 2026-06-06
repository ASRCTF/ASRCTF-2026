from math import gcd
from pathlib import Path

data = {}
for line in (Path(__file__).parent.parent / "dist" / "output.txt").read_text().splitlines():
    k, v = line.split(" = ")
    data[k.strip()] = int(v)

n, e1, e2, c1, c2 = data["n"], data["e1"], data["e2"], data["c1"], data["c2"]

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y

_, a, b = extended_gcd(e1, e2)

if b < 0:
    m = pow(c1, a, n) * pow(pow(c2, -b, n), -1, n) % n
else:
    m = pow(c1, a, n) * pow(c2, b, n) % n

print(m.to_bytes((m.bit_length() + 7) // 8, "big").decode())
