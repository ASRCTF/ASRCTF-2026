#!/usr/bin/env python3
import binascii
import hashlib
import subprocess
import sys
import textwrap
from pathlib import Path

WORD     = "Candleeggssweets"
N        = len(WORD)
NBITS    = N * 8
XOR_KEY  = 0xA3
FLAG     = "ASRCTF{but_th3_b1n4ry_n3v3r_l135}"
FLAG_KEY = 0x5C
OUT_BIN  = Path(__file__).parent.parent / "dist" / "cake"

MASK_BYTES   = hashlib.sha256(b"the_cake_is_a_lie_mask_v1").digest()[:N]
TARGET_BYTES = bytes(a ^ b for a, b in zip(WORD.encode(), MASK_BYTES))


def target_bits(target):
    bits = []
    for byte in target:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits


def build_netlist(bits):
    lines = [
        "module bake_unit_0x1 (",
        f"  input  wire [{NBITS-1}:0] D,",
        "  output wire        Q",
        ");",
        "",
    ]
    for j in range(NBITS):
        if bits[j] == 1:
            lines.append(f"  wire w{j:03d};")
            lines.append(f"  assign w{j:03d} = D[{j}];")
        else:
            lines.append(f"  wire w{j:03d}, nw{j:03d};")
            lines.append(f"  assign nw{j:03d} = ~D[{j}];")
            lines.append(f"  assign w{j:03d} = nw{j:03d};")
    lines.append("")
    current = [f"w{j:03d}" for j in range(NBITS)]
    level = 0
    while len(current) > 1:
        nxt = []
        for i in range(0, len(current) - 1, 2):
            wname = f"a{level}_{i//2:03d}"
            lines.append(f"  wire {wname};")
            lines.append(f"  assign {wname} = {current[i]} & {current[i+1]};")
            nxt.append(wname)
        if len(current) % 2 == 1:
            nxt.append(current[-1])
        current = nxt
        level += 1
    lines += ["", f"  assign Q = {current[0]};", "", "endmodule"]
    return "\n".join(lines)


def build_gate_c(bits):
    lines = []
    for j in range(NBITS):
        if bits[j] == 1:
            lines.append(f"    uint8_t w{j:03d} = (D >> {j}) & 1u;")
        else:
            lines.append(f"    uint8_t nw{j:03d} = (~(D >> {j})) & 1u;")
            lines.append(f"    uint8_t w{j:03d} = nw{j:03d};")
    lines.append("")
    current = [f"w{j:03d}" for j in range(NBITS)]
    level = 0
    while len(current) > 1:
        nxt = []
        for i in range(0, len(current) - 1, 2):
            wname = f"a{level}_{i//2:03d}"
            lines.append(f"    uint8_t {wname} = {current[i]} & {current[i+1]};")
            nxt.append(wname)
        if len(current) % 2 == 1:
            nxt.append(current[-1])
        current = nxt
        level += 1
    lines.append(f"    return (int){current[0]};")
    return "\n".join(lines)


def main():
    bits     = target_bits(TARGET_BYTES)
    netlist  = build_netlist(bits)
    blob     = bytes([b ^ XOR_KEY for b in netlist.encode()])
    crc      = binascii.crc32(blob) & 0xFFFFFFFF
    c_arr    = ", ".join(f"0x{b:02x}" for b in blob)
    gate_c   = build_gate_c(bits)
    enc_flag = bytes([b ^ FLAG_KEY for b in FLAG.encode()])
    enc_arr  = ", ".join(f"0x{b:02x}" for b in enc_flag)

    mask_lo = int.from_bytes(MASK_BYTES[:8],  'little')
    mask_hi = int.from_bytes(MASK_BYTES[8:16], 'little')

    c_src = textwrap.dedent(f"""\
        #include <stdio.h>
        #include <stdint.h>
        #include <string.h>
        #include <stdlib.h>

        typedef unsigned __int128 uint128_t;

        #define BLOB_LEN     {len(blob)}u
        #define XOR_KEY      0x{XOR_KEY:02X}u
        #define EXPECTED_CRC 0x{crc:08X}u
        #define FLAG_KEY     0x{FLAG_KEY:02X}u
        #define FLAG_LEN     {len(enc_flag)}u

        static const uint8_t blob[BLOB_LEN] = {{
            {c_arr}
        }};

        static const uint8_t enc_flag[FLAG_LEN] = {{
            {enc_arr}
        }};

        static uint32_t crc32_compute(const uint8_t *d, size_t n) {{
            uint32_t r = 0xFFFFFFFFu;
            for (size_t i = 0; i < n; i++) {{
                r ^= d[i];
                for (int k = 0; k < 8; k++)
                    r = (r >> 1) ^ (0xEDB88320u & -(r & 1u));
            }}
            return r ^ 0xFFFFFFFFu;
        }}

        static int bake_unit(uint128_t D) {{
        {gate_c}
        }}

        int main(void) {{
            if (crc32_compute(blob, BLOB_LEN) != EXPECTED_CRC) {{
                puts("The cake is a lie.");
                return 1;
            }}

            char *net = malloc(BLOB_LEN + 1);
            if (!net) return 1;
            for (size_t i = 0; i < BLOB_LEN; i++)
                net[i] = blob[i] ^ XOR_KEY;
            net[BLOB_LEN] = '\\0';
            puts(net);
            free(net);

            char inp[128];
            printf("Enter the secret ingredient: ");
            fflush(stdout);
            if (!fgets(inp, sizeof(inp), stdin)) return 1;
            size_t n = strlen(inp);
            if (n > 0 && inp[n-1] == '\\n') inp[--n] = '\\0';

            if (n != {N}) {{
                puts("The cake is a lie.");
                return 1;
            }}

            uint128_t raw = 0;
            for (int i = 0; i < {N}; i++)
                raw |= (uint128_t)(unsigned char)inp[i] << (i * 8);

            uint128_t mask = ((uint128_t){mask_hi}ULL << 64) | (uint128_t){mask_lo}ULL;
            uint128_t D = raw ^ mask;

            if (bake_unit(D)) {{
                char flag[FLAG_LEN + 1];
                for (size_t i = 0; i < FLAG_LEN; i++)
                    flag[i] = enc_flag[i] ^ FLAG_KEY;
                flag[FLAG_LEN] = '\\0';
                puts(flag);
            }} else {{
                puts("The cake is a lie.");
            }}
            return 0;
        }}
    """)

    c_path = OUT_BIN.parent / "_cake_stub.c"
    c_path.write_text(c_src)

    ret = subprocess.run(
        ["gcc", "-O1", "-o", str(OUT_BIN), str(c_path)],
        capture_output=True, text=True
    )
    if ret.returncode != 0:
        print("Compile error:", ret.stderr, file=sys.stderr)
        sys.exit(1)

    subprocess.run(["strip", "-s", str(OUT_BIN)], check=True)
    c_path.unlink()
    print(f"Built {OUT_BIN} ({OUT_BIN.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
