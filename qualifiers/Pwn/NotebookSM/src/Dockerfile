FROM debian AS builder

COPY chal.c /
RUN apt update && apt install -y gcc libseccomp-dev openssl socat
RUN gcc /chal.c -o /chal -fno-stack-protector -no-pie -lseccomp

COPY flag.txt .

RUN chmod 555 /chal && \
    chmod 444 /flag.txt

RUN useradd ctf

FROM scratch

WORKDIR /home/ctf

COPY --from=builder /chal /home/ctf
COPY --from=builder /usr/bin/socat /usr/bin/socat
COPY --from=builder /usr/bin/stdbuf /usr/bin/stdbuf

COPY --from=builder /usr/libexec/coreutils/libstdbuf.so /usr/libexec/coreutils/libstdbuf.so

COPY --from=builder /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
COPY --from=builder /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2 
COPY --from=builder /usr/lib/x86_64-linux-gnu/libseccomp.so.2 /usr/lib/x86_64-linux-gnu/libseccomp.so.2 
COPY --from=builder /usr/lib/x86_64-linux-gnu/libc.so.6 /usr/lib/x86_64-linux-gnu/libc.so.6 
COPY --from=builder /lib/x86_64-linux-gnu/libwrap.so.0 /lib/x86_64-linux-gnu/libwrap.so.0 
COPY --from=builder /lib/x86_64-linux-gnu/libssl.so.3 /lib/x86_64-linux-gnu/libssl.so.3 
COPY --from=builder /lib/x86_64-linux-gnu/libcrypto.so.3 /lib/x86_64-linux-gnu/libcrypto.so.3 
COPY --from=builder /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1 
COPY --from=builder /lib/x86_64-linux-gnu/libzstd.so.1  /lib/x86_64-linux-gnu/libzstd.so.1  

COPY --from=builder /chal /home/ctf/chal
COPY --from=builder /flag.txt /home/ctf/flag.txt

COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/shadow /etc/shadow
COPY --from=builder /etc/group /etc/group

USER ctf

EXPOSE 1337
CMD ["socat", "-x", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:stdbuf -i0 -o0 -e0 ./chal,pipes"]
