FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y gcc-multilib

WORKDIR /build
COPY chal.c .

RUN apt-get update && apt-get install -y socat libssl-dev && rm -rf /var/lib/apt/lists/*
RUN gcc chal.c -o chal -fno-stack-protector -z execstack -no-pie -lcrypto

FROM ubuntu:22.04

RUN useradd -m ctf
WORKDIR /home/ctf

COPY --from=builder /build/chal .
COPY flag.txt .

RUN apt-get update && apt-get install -y binutils socat libssl-dev && rm -rf /var/lib/apt/lists/*
RUN chown -R root:ctf /home/ctf && \
    chmod 755 /home/ctf/chal && \
    chmod 644 /home/ctf/flag.txt

USER ctf
EXPOSE 1337

CMD ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'stdbuf -i0 -o0 -e0 ./chal'"]