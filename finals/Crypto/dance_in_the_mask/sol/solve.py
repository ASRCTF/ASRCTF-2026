import numpy as np
from pathlib import Path

TRACES_PATH = Path(__file__).parent.parent / "dist" / "traces.npy"
LCG_A = 25214903917 & 0xFFFF
LCG_C = 11 & 0xFFFF
NUM_TRACES = 50000
SAMPLES = 200

def lcg(s):
    return (LCG_A * s + LCG_C) & 0xFFFF

def hw(x):
    return bin(x).count('1')

traces = np.load(TRACES_PATH)

fingerprints = traces[:, :16].mean(axis=1)
buckets = {}
seed_a = seed_b = None
for i, fp in enumerate(fingerprints):
    key = round(fp, 1)
    if key in buckets:
        seed_a, seed_b = buckets[key], i
        break
    buckets[key] = i

recovered_seed = None
for s in range(0x10000):
    st = s
    seeds = []
    for _ in range(NUM_TRACES):
        seeds.append(st)
        st = lcg(st)
    if seeds[seed_a] == seeds[seed_b]:
        recovered_seed = s
        break

rng = recovered_seed
mask_seeds = []
for _ in range(NUM_TRACES):
    mask_seeds.append(rng)
    rng = lcg(rng)

key_bytes = []
for byte_idx in range(4):
    sample_col = byte_idx % SAMPLES
    col = traces[:, sample_col]
    best_corr, best_k = -1, 0
    for k in range(256):
        hw_hyp = np.array([
            hw(k ^ (lcg(mask_seeds[i]) & 0xFF)) for i in range(NUM_TRACES)
        ], dtype=float)
        corr = abs(np.corrcoef(hw_hyp, col)[0, 1])
        if corr > best_corr:
            best_corr, best_k = corr, k
    key_bytes.append(best_k)

print(f"Recovered key word 0: {hex(int.from_bytes(bytes(key_bytes), 'little'))}")
