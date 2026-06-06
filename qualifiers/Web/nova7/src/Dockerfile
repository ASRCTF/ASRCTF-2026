FROM openjdk:8u121-jdk
WORKDIR /app

COPY chall.jar chall.jar
COPY flag.txt flag.txt

RUN chmod 644 flag.txt

RUN adduser --disabled-password --gecos "" --uid 1067 ctfuser
USER ctfuser

EXPOSE 8080

CMD ["java", "-jar", "./chall.jar"]