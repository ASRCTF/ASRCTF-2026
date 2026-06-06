import json
from pathlib import Path

ROOT = Path(__file__).parent.parent / "dist"
P    = 2**521 - 1

with open(ROOT / "bb84_transcripts.json") as f:
    data = json.load(f)

honest = []
for crew_id, ch in data.items():
    a, b = ch["alice_sifted_bits"], ch["bob_sifted_bits"]
    if sum(ai != bi for ai, bi in zip(a, b)) / len(a) < 0.1:
        honest.append(int(crew_id))

share_map = {}
for line in (ROOT / "shares.txt").read_text().splitlines():
    if not line or line.startswith("#"):
        continue
    x, y = line.split(":")
    share_map[int(x.strip())] = int(y.strip())

shares = [(x, share_map[x]) for x in honest]


def lagrange(pts, p):
    result = 0
    for i, (xi, yi) in enumerate(pts):
        num, den = 1, 1
        for j, (xj, _) in enumerate(pts):
            if i != j:
                num = (num * (-xj)) % p
                den = (den * (xi - xj)) % p
        result = (result + yi * num * pow(den, p - 2, p)) % p
    return result


secret = lagrange(shares, P)
print(secret.to_bytes((secret.bit_length() + 7) // 8, "big").decode())
