import random
from sage.all import *
from Crypto.Util.number import bytes_to_long


FLAG = b"ASRCTF{d0n7_b3_l4zy_wh3n_pr0v1ng_c0nf1d3nt14L_th1n9s!}"


def totally_normal_primality_test(n, k):
    if n == 2:
        return True

    if n % 2 == 0:
        return False

    test = 0
    while True:
        a = random.randint(1, n - 1)
        if pow(a, n - 1, n) != 1:
            return False
        test += 1

        if test == k:
            break

    return True

def main():
    w = bytes_to_long(FLAG)
    print("I'm lazy to generate my own prime, can you just generate one for me?")
    msg = input("Send me a p, please (format JSON var name 'p'): ")
    p = Integer(msg["p"])
    msg = input("Ugh, I'm too lazy to get q as well... (format JSON var name 'q'): ")
    q = Integer(msg["q"])

    if p < 2**512:
        print("Damn, I'd usually give a chance but that's SMALL small.")
        return

    if not totally_normal_primality_test(p, 4):
        print("Hey?? Do you know what a prime is??")
        return

    if (p-1).factor()[-1][0] < 2**384:
        print("Smooth operator~ But that's not what I'm looking for.")
        return

    print("Thanks, bae~")
    g = random.randint(1, p-1)
    r = random.randint(1, q-1)
    a = pow(g,r,p)

    print("Here's my a: ", a)
    msg = input("Send me an e (format JSON var name 'e'): ")
    e = Integer(msg["e"])

    if e > r.nbits() or e < 0:
        print("Hmm, I have a feeling you're not being very honest right now...")
        return

    z = (r + e*w) % q
    assert pow(g,z,p) == a*pow(g,w*e,p)
    print("Here's my z: ", z)
    print("You didn't see anything, did you~?")
    return

if __name__ == "__main__":
    main()
