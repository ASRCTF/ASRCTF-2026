FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl gnupg && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
    > /etc/apt/sources.list.d/mongodb-org-7.0.list

RUN apt-get update && \
    apt-get install -y \
    mongodb-org-server=7.0.0 \
    mongodb-org-shell=7.0.0 \
    mongodb-org-tools=7.0.0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN mkdir -p /data/db
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY mongod.conf /etc
COPY templates .
COPY static .
COPY app.py .
COPY create_database.py .
COPY /data/db /data/db/

RUN adduser --disabled-password --gecos "" --uid 1067 ctfuser && \
    chown -R ctfuser:ctfuser /app /data/db

USER ctfuser
    
EXPOSE 3000

ENV PYTHONUNBUFFERED=1

CMD sh -c "\
mongod --auth --dbpath /data/db --bind_ip 0.0.0.0 & \
sleep 3 && \
python3 create_database.py && \
sleep 3 && \
python3 app.py \
"

# Expose port after adding admin user
EXPOSE 27017