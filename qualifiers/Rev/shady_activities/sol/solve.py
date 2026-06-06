import struct
import sys
from pathlib import Path

BINARY    = Path(__file__).parent.parent / "dist" / "shady_activities"
FLAG_LEN  = 40
SPV_MAGIC = 0x07230203
SPV_WORDS = 404
ID_ENC_BASE = 12
ID_KEY_BASE = 52


def find_spv(raw):
    for i in range(0, len(raw) - 4, 4):
        if struct.unpack_from("<I", raw, i)[0] == SPV_MAGIC:
            return struct.unpack_from("<" + "I" * SPV_WORDS, raw, i)


def parse_constants(words):
    enc_f, key_i = {}, {}
    i = 5
    while i < len(words):
        wc, opcode = words[i] >> 16, words[i] & 0xFFFF
        if opcode == 43 and wc == 4:
            tid, rid, val = words[i+1], words[i+2], words[i+3]
            if tid == 4 and ID_ENC_BASE <= rid < ID_ENC_BASE + FLAG_LEN:
                enc_f[rid - ID_ENC_BASE] = struct.unpack("<f", struct.pack("<I", val))[0]
            if tid == 3 and ID_KEY_BASE <= rid < ID_KEY_BASE + FLAG_LEN:
                key_i[rid - ID_KEY_BASE] = val
        i += wc
    return enc_f, key_i


def main():
    raw = (Path(sys.argv[1]) if len(sys.argv) > 1 else BINARY).read_bytes()
    enc_f, key_i = parse_constants(find_spv(raw))
    print(bytes(round(enc_f[i] * 255.0) ^ key_i[i] for i in range(FLAG_LEN)).decode())


if __name__ == "__main__":
    main()
