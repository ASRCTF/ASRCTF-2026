from pathlib import Path

HORSE_ONE  = "🐴"
COL_ORDER  = [1, 3, 0, 4, 2]
VIGENERE_KEY = "SHADOWMERE"


def emoji_decode(line):
    return "".join(chr(int("".join("1" if c == HORSE_ONE else "0" for c in g), 2))
                   for g in line.strip().split(" "))


def columnar_decrypt(ctext, col_order):
    n = len(col_order)
    num_rows = len(ctext) // n
    cols = {col: ctext[i*num_rows:(i+1)*num_rows] for i, col in enumerate(col_order)}
    return "".join(cols[c][r] for r in range(num_rows) for c in range(n)).rstrip("~")


def vigenere_decrypt(text, key):
    result, ki = [], 0
    for ch in text:
        if 32 <= ord(ch) <= 126:
            p = (ord(ch) - 32 - (ord(key[ki % len(key)]) - 32)) % 95 + 32
            result.append(chr(p)); ki += 1
        else:
            result.append(ch)
    return "".join(result)


dispatch = Path("dispatch.txt").read_text(encoding="utf-8")
emoji_line = next(l for l in dispatch.splitlines()
                  if l and all(c in (HORSE_ONE, "🐎", " ") for c in l))

print(vigenere_decrypt(columnar_decrypt(emoji_decode(emoji_line), COL_ORDER), VIGENERE_KEY))
