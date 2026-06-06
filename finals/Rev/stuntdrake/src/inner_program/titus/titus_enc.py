msg = "Please don't snipe me"
enc = []
key = "0x6f"
for char in msg:
    enc.append(ord(char) ^ int(key, 16))

final_enc = []
for char in enc:
    final_enc.append(chr((char + 4) %26 + ord("A")))

print(final_enc)
