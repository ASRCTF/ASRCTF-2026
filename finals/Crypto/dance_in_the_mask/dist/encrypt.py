import numpy as np
import os

LCG_A = 25214903917 & 0xFFFF
LCG_C = 11 & 0xFFFF

def lcg(s):
    return (LCG_A * s + LCG_C) & 0xFFFF

def hw(x):
    return bin(x).count('1')

def capture(key_bytes, mask_seed, n_samples=200):
    state = mask_seed
    out = []
    for i in range(n_samples):
        state = lcg(state)
        mask = state & 0xFF
        b = (key_bytes >> (8 * (i % 4))) & 0xFF
        out.append(hw(b ^ mask) + float(np.random.normal(0, 1.5)))
    return out
