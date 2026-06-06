import os
import sys

FLAG = os.environ.get("FLAG", "ASRCTF{pr1m35_4r3_qu1t3_1ntr1gu1ng}")

n = 1296001987165015643369032371289
g = 5
h = 942170777578027229169443183566


def commit_open(C, m, r):
    return pow(g, m, n) * pow(h, r, n) % n == C


def main():
    print("=== CryptoVault Commitment Lottery ===")
    print(f"n = {n}")
    print(f"g = {g}")
    print(f"h = {h}")
    print()
    print("Send your commitment C (integer):")

    try:
        C = int(input("> ").strip())
        assert 1 < C < n
    except Exception:
        print("invalid commitment"); sys.exit(1)

    print("Open it as (m1, r1):")
    try:
        m1, r1 = map(int, input("> ").strip().split())
        assert 0 <= m1 < n and 0 <= r1 < n
    except Exception:
        print("invalid opening"); sys.exit(1)

    if not commit_open(C, m1, r1):
        print("bad opening"); sys.exit(1)

    print("Now open the same C to a different message (m2, r2):")
    try:
        m2, r2 = map(int, input("> ").strip().split())
        assert 0 <= m2 < n and 0 <= r2 < n
    except Exception:
        print("invalid opening"); sys.exit(1)

    if not commit_open(C, m2, r2):
        print("bad opening"); sys.exit(1)

    if m1 == m2:
        print("m1 == m2, binding holds."); sys.exit(1)

    print(f"Binding broken. {FLAG}")


if __name__ == "__main__":
    main()
