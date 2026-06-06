import socket

HOST = "" #change this accordingly
PORT = 12345


def compute_forgery(n, g, h):
    raise NotImplementedError
    

def main():
    with socket.create_connection((HOST, PORT)) as s:
        f = s.makefile("rw", buffering=1)

        def recv():  return f.readline().strip()
        def send(x): f.write(str(x) + "\n")

        recv()
        n = int(recv().split()[-1])
        g = int(recv().split()[-1])
        h = int(recv().split()[-1])
        recv()
        recv()

        C, m1, r1, m2, r2 = compute_forgery(n, g, h)

        send(C)
        recv()
        send(f"{m1} {r1}")
        recv()
        send(f"{m2} {r2}")

        print(recv())


if __name__ == "__main__":
    main()
