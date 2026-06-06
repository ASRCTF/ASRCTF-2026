import random
import json
from secret import flag

P      = 2**521 - 1
secret = int.from_bytes(flag, "big")
k, n   = 5, 7

random.seed(42)
coeffs = [secret] + [random.randint(1, P - 1) for _ in range(k - 1)]


def poly_eval(c, x, p):
    v = 0
    for ci in reversed(c):
        v = (v * x + ci) % p
    return v


shares = [(i, poly_eval(coeffs, i, P)) for i in range(1, n + 1)]

random.seed(99)
corrupt = list(shares)
for idx in [2, 5]:
    corrupt[idx] = (
        shares[idx][0],
        (shares[idx][1] + random.randint(10**75, 10**76)) % P,
    )


def bb84_channel(nq, eve, seed):
    rng = random.Random(seed)
    ab  = [rng.randint(0, 1)      for _ in range(nq)]
    aba = [rng.choice(["+", "x"]) for _ in range(nq)]
    if eve:
        eb = [rng.choice(["+", "x"]) for _ in range(nq)]
        tx = [ab[i] if eb[i] == aba[i] else rng.randint(0, 1) for i in range(nq)]
    else:
        tx = ab
    bba = [rng.choice(["+", "x"]) for _ in range(nq)]
    bb  = [tx[i] if bba[i] == aba[i] else rng.randint(0, 1) for i in range(nq)]
    sifted = [
        {"qubit": i, "basis": aba[i], "alice": ab[i], "bob": bb[i]}
        for i in range(nq) if aba[i] == bba[i]
    ]
    return aba, bba, sifted


transcript = {}
for crew in range(1, 8):
    aba, bba, sifted = bb84_channel(40, crew in [3, 6], seed=crew * 100)
    transcript[str(crew)] = {
        "crew_member":       crew,
        "alice_bases":       aba,
        "bob_bases":         bba,
        "sifted_positions":  [s["qubit"] for s in sifted],
        "alice_sifted_bits": [s["alice"] for s in sifted],
        "bob_sifted_bits":   [s["bob"]   for s in sifted],
    }

with open("bb84_transcripts.json", "w") as f:
    json.dump(transcript, f, indent=2)

with open("shares.txt", "w") as f:
    f.write(f"# n=7  k=5  prime=2^521-1\n")
    for x, y in corrupt:
        f.write(f"{x} : {y}\n")
