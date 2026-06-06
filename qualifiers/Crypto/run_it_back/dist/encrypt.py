import sys

ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789_"
M = len(ALPHA)
KEY = [31, 29, 0, 6, 11, 3, 30, 19, 31, 5, 15, 5, 24, 20, 30, 30, 23, 4, 31, 32, 13, 31, 25]

def encrypt(s):
    if len(s) != len(KEY):
        raise ValueError(f"input must be exactly {len(KEY)} characters")
    if not all(c in ALPHA for c in s):
        raise ValueError("input must only contain lowercase letters, digits, or underscores")
    n = len(s)
    v = [ALPHA.index(c) for c in s]
    return ''.join(ALPHA[(11 * v[(i - 1) % n] + 7 * v[(i + 1) % n] + KEY[i]) % M] for i in range(n))

if __name__ == "__main__":
    print(encrypt(sys.argv[1]))
