FROM debian:bookworm-slim

RUN useradd -m ctf
WORKDIR /home/ctf

RUN apt-get update && \
    apt-get install -y nodejs npm socat && \
    rm -rf /var/lib/apt/lists/*

COPY jail.js .
COPY flag.txt .

RUN chown -R root:ctf /home/ctf && \
    chmod 755 /home/ctf/jail.js && \
    chmod 644 /home/ctf/flag.txt

USER ctf

EXPOSE 1337
CMD ["socat", "-v", "TCP-LISTEN:1337,nodelay,reuseaddr,fork", "EXEC:node jail.js"]