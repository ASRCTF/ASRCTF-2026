FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
  apt-get install -y python3 python3-pip && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY templates templates 
COPY app.py .
COPY flag.txt .

RUN chmod -R 555 /app

RUN adduser --disabled-password --gecos "" --uid 1067 ctfuser

USER ctfuser

EXPOSE 3000

ENV PYTHONUNBUFFERED=1

CMD ["python3", "app.py"]
