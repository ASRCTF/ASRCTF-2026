text = open("🥀✌️💔.txt", encoding="utf-8").read()

heart = []

for i, c in enumerate(text[:-1]):
    if c == "💔":
        cp = ord(text[i + 1])
        if 0xE0100 <= cp <= 0xE01EF:
            heart.append(cp - 0xE0100)

print(bytes((x - 67) % 240 for x in heart).decode())
