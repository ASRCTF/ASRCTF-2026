CC := gcc
CFLAGS := -O0 -g -Wall -Wextra -fno-stack-protector -fno-pie -fcf-protection=none \
	-fno-plt -mfunction-return=thunk-extern
LDFLAGS := -no-pie -nostartfiles -Wl,-z,relro,-z,now -Wl,--section-start=.gate=0x405000

.PHONY: all clean check-gadgets

all: chal

chal: chal.c return_thunk.S
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

check-gadgets: chal
	@objdump -d -M intel chal | grep -nE '\bret[q]?\b' || true
	@echo
	@objdump -d -M intel chal | grep -nE '<gate_nop>|<gate_echo>|jmp.*r11|call.*__x86_return_thunk'

clean:
	rm -f chal
