FROM sagemath/sagemath:latest

RUN apt-get update && apt-get install -y socat
RUN sage -pip install pycryptodome

WORKDIR /challenge

COPY chall.sage .
COPY secrets.py .

EXPOSE 1337

CMD socat TCP-LISTEN:1337,reuseaddr,fork EXEC:"sage chall.sage"
