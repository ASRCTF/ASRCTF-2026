ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789_"
M = len(ALPHA)
KEY = [31, 29, 0, 6, 11, 3, 30, 19, 31, 5, 15, 5, 24, 20, 30, 30, 23, 4, 31, 32, 13, 31, 25] 
n = len(KEY)

def modinv(a, m):
    g, x, b, y = m, 0, a % m, 1
    while b:
        q = g // b
        g, b = b, g - q * b
        x, y = y, x - q * y
    return x % m if g == 1 else None

mat = [[0] * n for _ in range(n)]
for i in range(n):
    mat[i][(i - 1) % n] = (-11) % M
    mat[i][i] = (mat[i][i] + 1) % M
    mat[i][(i + 1) % n] = (mat[i][(i + 1) % n] - 7) % M

aug = [mat[i] + [KEY[i]] for i in range(n)]

r = 0
for c in range(n):
    pivot = next((i for i in range(r, n) if aug[i][c] % M), None)
    if pivot is None:
        continue
    aug[r], aug[pivot] = aug[pivot], aug[r]
    inv = modinv(aug[r][c], M)
    aug[r] = [(x * inv) % M for x in aug[r]]
    for i in range(n):
        if i != r and aug[i][c]:
            f = aug[i][c]
            aug[i] = [(aug[i][j] - f * aug[r][j]) % M for j in range(n + 1)]
    r += 1

sol = ''.join(ALPHA[aug[i][-1]] for i in range(n))
print(f"ASRCTF{{{sol}}}")
