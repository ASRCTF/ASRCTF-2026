import hashlib
from pathlib import Path

data = {}
for line in (Path(__file__).parent.parent / "dist" / "output.txt").read_text().splitlines():
    k, v = line.split(" = ", 1)
    data[k.strip()] = v.strip()

msg1 = data["msg1"].encode()
msg2 = data["msg2"].encode()
r  = int(data["r"],  16)
s1 = int(data["s1"], 16)
s2 = int(data["s2"], 16)
encrypted_flag = bytes.fromhex(data["encrypted_flag"])

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

z1 = int.from_bytes(hashlib.sha256(msg1).digest(), "big") % n
z2 = int.from_bytes(hashlib.sha256(msg2).digest(), "big") % n

k = (z1 - z2) * pow(s1 - s2, -1, n) % n
d = (s1 * k - z1) * pow(r, -1, n) % n

d_bytes = d.to_bytes(32, "big")
mask = (hashlib.sha256(d_bytes).digest() + d_bytes)[:len(encrypted_flag)]
print(bytes(a ^ b for a, b in zip(encrypted_flag, mask)).decode())
