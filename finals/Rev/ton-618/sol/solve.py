import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent

def decode_path(clock_dir):
    files = sorted(clock_dir.iterdir(), key=lambda p: p.name)
    bits = [int(p.stat().st_mtime) % 2 for p in files]
    chars = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        chars.append(chr(byte))
    return "".join(chars)

def solve_subset_sum(binary_path):
    N = [
        1020544596, 1355972289, 1391647585, 1405480800,
        1423944875, 1437982291, 1457513853, 1457942829,
        1499394254, 1504263996, 1643476878, 1657334267,
        1674293055, 1717735726, 1746059110, 1781248712,
        1829341823, 1959926481, 1966240608, 1999302076,
    ]
    T = 11744788681
    half = len(N) // 2

    left = {}
    for mask in range(1 << half):
        s = sum(N[i] for i in range(half) if (mask >> i) & 1)
        left[s] = mask

    for mask in range(1 << (len(N) - half)):
        s = sum(N[half + i] for i in range(len(N) - half) if (mask >> i) & 1)
        complement = T - s
        if complement in left:
            full_mask = left[complement] | (mask << half)
            result = subprocess.check_output(
                [str(binary_path)], input=str(full_mask).encode()
            )
            return result.decode().strip()

    return None

dist = ROOT / "dist" / "dist"
rel_path = decode_path(dist / "clock")
flag = solve_subset_sum(dist / rel_path)
print(flag)
