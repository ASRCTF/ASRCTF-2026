FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge

# Copy only the necessary binaries from dist
COPY ./dist/chal .
COPY ./dist/libc.so.6 .
COPY ./dist/ld-linux-x86-64.so.2 .

# Copy only the flag from sol
COPY ./sol/flag.txt .

# Ensure permissions are correct
RUN chmod +x chal ld-linux-x86-64.so.2

CMD ["sh", "-c", "socat TCP-LISTEN:1337,reuseaddr,fork EXEC:'stdbuf -i0 -o0 -e0 ./chal'"]