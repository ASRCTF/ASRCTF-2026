import random
from sage.all import *
from Crypto.Util.number import bytes_to_long


FLAG = b"ASRCTF{???}"


def totally_up_to_date_primality_test(n, k):
    # Hmmm why should I tell you?
    return 
    
def main():
    w = bytes_to_long(FLAG)
    print("I'm lazy to generate my own prime, can you just generate one for me?")
    msg = input("Send me a p, please: ")
    p = msg["p"]

    if p < 2**512:
        print("Damn, I'd usually give a chance but that's SMALL small.")
        return

    if not totally_up_to_date_primality_test(p, 1024):
        print("Hey?? Do you know what a prime is??")
        return

    if (p-1).factor()[-1][0] < 2**384:
        print("Smooth operator~ But that's not what I'm looking for.")
        return

    print("Thanks, bae~")
    g = random.randint(1, p-1)
    q = g.multiplicative_order()
    r = random.randint(1, q-1)
    a = pow(g,r,p)

    print("Here's my a: ", a)
    msg = input("Send me an e: ")
    e = msg["e"]

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
