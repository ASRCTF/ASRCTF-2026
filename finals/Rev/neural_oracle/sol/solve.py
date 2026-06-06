import struct
import numpy as np
import tensorflow as tf
from pathlib import Path

BIN = Path(__file__).parent.parent / "dist" / "oracle.bin"


def carve(raw: bytes) -> bytes:
    assert raw[:4] == b"\x7fMLO", "bad magic"
    offset = struct.unpack_from("<I", raw, 4)[0]
    size   = struct.unpack_from("<I", raw, 8)[0]
    return raw[offset : offset + size]


def extract_flag(tflite: bytes) -> str:
    tmp = "/tmp/_oracle.tflite"
    with open(tmp, "wb") as f:
        f.write(tflite)

    interp = tf.lite.Interpreter(model_path=tmp)
    interp.allocate_tensors()

    details = interp.get_tensor_details()
    bias    = None
    for t in details:
        if t["shape"].tolist() == [80]:
            bias = interp.get_tensor(t["index"])
            break
    x_star = -bias[:40]
    return bytes(round(float(v) * 255) for v in x_star).decode()


if __name__ == "__main__":
    raw    = BIN.read_bytes()
    tflite = carve(raw)
    flag   = extract_flag(tflite)
    print(f"Flag: {flag}")
