FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
  apt-get install -y python3 python3-pip && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN mkdir -p /data/db
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY templates templates 
COPY notes notes
COPY app.py .
COPY flag.txt .

RUN adduser --disabled-password --gecos "" --uid 1067 ctfuser
RUN chown -R ctfuser:ctfuser /app/notes
USER ctfuser

EXPOSE 3000

ENV PYTHONUNBUFFERED=1

CMD ["python3", "app.py"]