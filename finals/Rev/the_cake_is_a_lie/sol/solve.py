import hashlib
import re
import subprocess
from pathlib import Path

BIN      = Path(__file__).parent.parent / "dist" / "cake"
XOR_KEY  = 0xA3
FLAG_KEY = 0x5C
MASK     = hashlib.sha256(b"the_cake_is_a_lie_mask_v1").digest()[:16]


def extract_blob() -> bytes:
    result = subprocess.run(
        ["readelf", "-x", ".rodata", str(BIN)],
        capture_output=True, text=True, check=True
    )
    all_bytes = []
    for line in result.stdout.splitlines():
        m = re.match(r"\s+0x[0-9a-f]+\s+((?:[0-9a-f]{8}\s*){1,4})", line)
        if m:
            hexstr = m.group(1).replace(" ", "")
            for i in range(0, len(hexstr), 2):
                all_bytes.append(int(hexstr[i:i+2], 16))
    data = bytes(all_bytes)
    needle = bytes([b ^ XOR_KEY for b in b"module"])
    idx = data.find(needle)
    if idx == -1:
        raise RuntimeError("Could not locate encrypted blob in .rodata")
    return data[idx:]


def extract_enc_flag() -> bytes:
    result = subprocess.run(
        ["readelf", "-x", ".rodata", str(BIN)],
        capture_output=True, text=True, check=True
    )
    all_bytes = []
    for line in result.stdout.splitlines():
        m = re.match(r"\s+0x[0-9a-f]+\s+((?:[0-9a-f]{8}\s*){1,4})", line)
        if m:
            hexstr = m.group(1).replace(" ", "")
            for i in range(0, len(hexstr), 2):
                all_bytes.append(int(hexstr[i:i+2], 16))
    data = bytes(all_bytes)
    needle   = bytes([b ^ FLAG_KEY for b in b"ASRCTF{"])
    enc_brace = ord("}") ^ FLAG_KEY
    idx = data.find(needle)
    if idx == -1:
        raise RuntimeError("Could not locate encrypted flag in .rodata")
    end = idx + len(needle)
    while end < len(data) and data[end] != enc_brace:
        end += 1
    return data[idx:end + 1]


def solve_netlist(netlist: str) -> str:
    m = re.search(r"input\s+wire\s+\[(\d+):0\]\s+D", netlist)
    if not m:
        raise RuntimeError("Could not parse input width from netlist")
    nbits  = int(m.group(1)) + 1
    nchars = nbits // 8

    target_bits = [None] * nbits
    for line in netlist.splitlines():
        m2 = re.match(r"\s*assign\s+w\d+\s*=\s*D\[(\d+)\];", line)
        if m2:
            target_bits[int(m2.group(1))] = 1
        m2 = re.match(r"\s*assign\s+nw\d+\s*=\s*~D\[(\d+)\];", line)
        if m2:
            target_bits[int(m2.group(1))] = 0

    target_bytes = bytearray()
    for i in range(nchars):
        val = sum(target_bits[i*8 + b] << b for b in range(8))
        target_bytes.append(val)

    secret = bytes(a ^ b for a, b in zip(target_bytes, MASK[:nchars]))
    return secret.decode()


def main():
    blob    = extract_blob()
    netlist = bytes([b ^ XOR_KEY for b in blob]).decode()
    secret  = solve_netlist(netlist)
    print(f"Secret ingredient: {secret}")

    enc_flag = extract_enc_flag()
    flag = bytes([b ^ FLAG_KEY for b in enc_flag]).decode()
    print(f"FLAG: {flag}")

    proc = subprocess.run(
        [str(BIN)],
        input=secret + "\n",
        capture_output=True, text=True
    )
    flag_lines = [l for l in proc.stdout.splitlines() if "ASRCTF" in l]
    if flag_lines:
        print(f"Verified: {flag_lines[0]}")
    else:
        print("Binary output:", proc.stdout)


if __name__ == "__main__":
    main()
