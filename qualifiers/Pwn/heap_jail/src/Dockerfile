FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge

COPY dist/chal .
COPY dist/libc.so.6 .
COPY dist/ld-linux-x86-64.so.2 .
COPY sol/flag.txt .

RUN chmod +x chal ld-linux-x86-64.so.2 libc.so.6 && \
    chmod 444 flag.txt

CMD ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'stdbuf -i0 -o0 -e0 ./chal'"]