FROM ubuntu:22.04

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf
WORKDIR /home/ctf

COPY dist/chal .
COPY sol/flag.txt .

RUN chown -R root:ctf /home/ctf && \
    chmod 750 /home/ctf/chal && \
    chmod 440 /home/ctf/flag.txt

USER ctf
EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./chal,stderr"]
