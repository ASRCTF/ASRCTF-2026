CC = gcc
CFLAGS = -O0 -no-pie -fno-stack-protector -z noexecstack -Wno-unused-result

all: chal

chal: chal.c
	$(CC) $(CFLAGS) chal.c -o chal

clean:
	rm -f chal
