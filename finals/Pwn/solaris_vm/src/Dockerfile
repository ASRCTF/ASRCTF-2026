# Stage 1: Build the VM binary
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y gcc make

WORKDIR /build
COPY src/chal.c .
COPY src/Makefile .

RUN make

# Stage 2: Final lightweight execution environment
FROM ubuntu:22.04

# Install python3 for the server wrapper and socat for networking
RUN apt-get update && apt-get install -y python3 socat && rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf
WORKDIR /home/ctf

# Copy the compiled VM binary, flag, and the Python server wrapper
COPY --from=builder /build/chal .
COPY src/server.py .
COPY sol/flag.txt .

# Ensure proper permissions
RUN chown -R root:ctf /home/ctf && \
    chmod 750 /home/ctf/chal && \
    chmod 750 /home/ctf/server.py && \
    chmod 440 /home/ctf/flag.txt

USER ctf
EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 server.py,stderr"]
