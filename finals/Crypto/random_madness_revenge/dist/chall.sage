import random
from Crypto.Util.number import bytes_to_long
from hashlib import md5
from os import urandom


FLAG = b"ASRCTF{???}"
R = RealField(168)
x = R(0.785) + R(0.2) * R.random_element()


random.seed(bytes_to_long(FLAG))
LEAK = [bytes_to_long(random.randbytes(32)) for _ in range(625)]
good_luck = [cos(x)] * 24 + [sin(x)] * 1
random.shuffle(good_luck)

have_fun = []
for i in range(0, len(LEAK), 25):
    random.shuffle(good_luck)
    have_fun.append([LEAK[i+j] * good_luck[j] for j in range(25)])
    
    
print(f"x: {x}, res: {have_fun}")
