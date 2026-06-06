FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
  apt-get install -y python3 python3-pip \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxcb1 \
    libx11-6 && \
  rm -rf /var/lib/apt/lists/*
  
COPY templates templates
COPY app.py app.py
COPY bot.py bot.py
COPY flag.txt flag.txt
COPY requirements.txt requirements.txt

RUN chmod -R 555 /app 

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt
RUN adduser --disabled-password --gecos "" --uid 1067 ctfuser
    
ENV PYTHONUNBUFFERED=1
USER ctfuser

EXPOSE 3000

CMD ["python3", "app.py"]
