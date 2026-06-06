with open("../dist/speedrun.nes", "rb") as f:
    data = f.read()

konami = [0, 0, 1, 1, 2, 3, 2, 3, 4, 5]
chr_rom = data[16 + data[4] * 16384:]

print("".join(
    chr(chr_rom[((i * 37 + konami[i % 10] * 13 + 7) % 512) * 16])
    for i in range(45)
))
