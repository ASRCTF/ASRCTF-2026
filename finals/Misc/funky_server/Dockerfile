FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pyfiglet rich

WORKDIR /home/ctf

COPY dist/server.py .
COPY sol/flag.txt .
COPY sol/sus.txt .

RUN useradd -m ctf && \
    chown -R root:root /home/ctf && \
    chmod -R 755 /home/ctf && \
    chmod 444 flag.txt sus.txt

USER ctf

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 /home/ctf/server.py"]
