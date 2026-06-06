with open("ciphertext.txt", "rb") as file:
    ct = file.read()

LENGTH = len(ct)

with open("keys.txt", "rb") as file:
    while True:
        key = file.read(LENGTH)
        if not key:
            break
        ct = bytes([c ^ k for c, k in zip(ct, key)])

print(ct)
