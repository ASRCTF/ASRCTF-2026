FROM python:3.10-slim

# Install socat for TCP-to-stdin/stdout bridging
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged CTF user
RUN useradd -m -d /home/ctf -s /bin/sh ctf

# Copy challenge files
COPY server.py /home/ctf/server.py
COPY flag.txt  /home/ctf/flag.txt

# Set ownership and permissions
RUN chown -R root:ctf /home/ctf && \
    chmod 555 /home/ctf/server.py && \
    chmod 444 /home/ctf/flag.txt

WORKDIR /home/ctf
USER ctf

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 /home/ctf/server.py"]
