import base64
import requests

BASE = "http://localhost:3000" #where i hosted the server on during my testing

requests.get(f"{BASE}/")

requests.get(f"{BASE}/robots.txt")

r = requests.get(f"{BASE}/the-map-was-here-all-along")
hint = base64.b64decode(r.text).decode()
sequence = [int(x) for x in hint.split(": ")[1].split(",")]

requests.post(f"{BASE}/knock", json={"sequence": sequence})

r = requests.get(f"{BASE}/finally")
key_bytes = bytes.fromhex(r.headers["X-Key"])
ciphertext = bytes.fromhex(r.text)
flag = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(ciphertext))
print(flag.decode())
