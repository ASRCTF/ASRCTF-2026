FROM ubuntu:25.04

COPY ./chal /srv/app/run
COPY ./entry.sh /srv/app/entry.sh
COPY ./flag.txt /srv/app/flag.txt
RUN chmod 555 /srv/app/run
RUN chmod 444 /srv/app/flag.txt
RUN chmod 555 /srv/app/entry.sh
RUN apt-get update && \
    apt-get install -y socat adduser && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 1001 nonroot && \
    adduser --uid 1001 --gid 1001 --disabled-password --gecos "" nonroot && \
    echo 'nonroot ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
USER 1001

WORKDIR /srv/app

EXPOSE 8080

CMD [ "/srv/app/entry.sh" ]