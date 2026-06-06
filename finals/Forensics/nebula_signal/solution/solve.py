import sys
from PIL import Image


def decode(path: str) -> str:
    img  = Image.open(path).convert("RGB")
    w, h = img.size
    px   = img.load()
    pixels = [px[x, y] for y in range(h) for x in range(w)]

    bits = []
    for i, (r, g, b) in enumerate(pixels):
        method = i % 4
        if method == 0:        
            bits.append(r & 1)
        elif method == 1:   
            bits.append(b & 1)
        elif method == 2:  
            bits.append(g & 1)
        else:  
            bits.append((r + g + b) % 2)

    chars = []
    for i in range(0, len(bits) - 7, 8):
        val = int("".join(str(b) for b in bits[i:i+8]), 2)
        if val == 0:
            break
        chars.append(chr(val))

    return "".join(chars)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "deep_field_NGC7293.png"
    flag = decode(path)
    print(f"Flag: {flag}")
