import math
import subprocess
import sys

n  = 1296001987165015643369032371289
g  = 5
h  = 942170777578027229169443183566

p1, p2, p3 = 6000003067, 12000006133, 18000009199

SUBGROUPS = [
    (p1, 6000003066, {2: 1, 3: 1, 31: 1, 61: 1, 528821: 1}),
    (p2, 4000002044, {2: 2,       31: 1, 61: 1, 528821: 1}),
    (p3, 9000004599, {3: 2,       31: 1, 61: 1, 528821: 1}),
]


def bsgs(gamma, target, p, q):
    if q == 1:
        return 0
    m = math.isqrt(q) + 1
    baby = {}
    cur = 1
    for j in range(m):
        baby[target * cur % p] = j
        cur = cur * gamma % p
    gm  = pow(gamma, m, p)
    cur = 1
    for i in range(1, m + 2):
        cur = cur * gm % p
        if cur in baby:
            x = (i * m - baby[cur]) % q
            if pow(gamma, x, p) == target:
                return x
    return None


def pohlig_hellman(g, h, p, order, factors):
    residues, moduli = [], []
    for q, e in factors.items():
        qe    = q ** e
        gi    = pow(g, order // qe, p)
        hi    = pow(h, order // qe, p)
        xi    = 0
        gamma = pow(gi, qe // q, p)
        for k in range(e):
            hk = pow(pow(gi, -xi, p) * hi % p, qe // q ** (k + 1), p)
            dk = bsgs(gamma, hk, p, q)
            assert dk is not None
            xi += dk * q ** k
        residues.append(xi % qe)
        moduli.append(qe)
    M = math.prod(moduli)
    return sum(r * (M // m) * pow(M // m, -1, m) for r, m in zip(residues, moduli)) % M


def crt2(r1, m1, r2, m2):
    d   = math.gcd(m1, m2)
    lcm = m1 * m2 // d
    t   = (r2 - r1) // d * pow(m1 // d, -1, m2 // d) % (m2 // d)
    return (r1 + m1 * t) % lcm, lcm


def recover_trapdoor():
    r, m = None, None
    for p, order, factors in SUBGROUPS:
        xi   = pohlig_hellman(g % p, h % p, p, order, factors)
        r, m = (xi, order) if r is None else crt2(r, m, xi, order)
    assert pow(g, r, n) == h
    return r, m


def forge(x_eff, lam, m1=0, m2=1):
    r1 = 13371337133713
    C  = pow(g, m1, n) * pow(h, r1, n) % n
    r2 = (x_eff * r1 + m1 - m2) * pow(x_eff, -1, lam) % lam
    assert pow(g, m2, n) * pow(h, r2, n) % n == C
    return C, m1, r1, m2, r2


def main():
    x_eff, lam = recover_trapdoor()

    C, m1, r1, m2, r2 = forge(x_eff, lam)

    server = subprocess.Popen(
        [sys.executable, "../src/server.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )
    inp    = "\n".join([str(C), f"{m1} {r1}", f"{m2} {r2}"]) + "\n"
    out, _ = server.communicate(inp)
    for line in out.splitlines():
        if "ASRCTF" in line or "Binding" in line:
            print(line)


if __name__ == "__main__":
    main()
