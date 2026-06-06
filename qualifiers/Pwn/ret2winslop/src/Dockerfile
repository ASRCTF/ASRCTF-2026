# Stage 1: Build the binary
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y gcc-multilib

WORKDIR /build
COPY src/chal.c .

RUN gcc chal.c -o chal \
    -fno-stack-protector \
    -z relro -z now \
    -z noexecstack \
    -no-pie

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf
WORKDIR /home/ctf

COPY dist/chal .
COPY sol/flag.txt .

RUN chown -R root:ctf /home/ctf && \
    chmod 750 /home/ctf/chal && \
    chmod 444 /home/ctf/flag.txt

USER ctf
EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./chal,stderr"]
