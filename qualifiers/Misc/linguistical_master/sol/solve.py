import hashlib
from pathlib import Path
data = {}
for line in (Path(__file__).parent.parent / "dist" / "output.txt").read_text().splitlines():
    k, v = line.split(" = ", 1)
    data[k.strip()] = v.strip()

ciphertext     = data["ciphertext"]
encrypted_flag = bytes.fromhex(data["encrypted_flag"])

dec_map = {
    'i': 'a', 'd': 'b', 'y': 'c', 'p': 'd', 'f': 'e',
    'j': 'f', 's': 'g', 'w': 'h', 'v': 'i', 'h': 'j',
    't': 'k', 'x': 'l', 'e': 'm', 'm': 'n', 'k': 'o',
    'z': 'p', 'a': 'q', 'l': 'r', 'g': 's', 'u': 't',
    'n': 'u', 'q': 'v', 'o': 'w', 'c': 'x', 'b': 'y',
    'r': 'z',
}

def decrypt(text):
    result = []
    for c in text:
        lo = c.lower()
        if lo in dec_map:
            plain = dec_map[lo]
            result.append(plain.upper() if c.isupper() else plain)
        else:
            result.append(c)
    return ''.join(result)

plaintext = decrypt(ciphertext)
print(plaintext)

key       = hashlib.sha256(plaintext.encode()).digest()
xor_key   = (key * ((len(encrypted_flag) // len(key)) + 1))[:len(encrypted_flag)]
flag      = bytes(a ^ b for a, b in zip(encrypted_flag, xor_key)).decode()
print("Flag:", flag)
