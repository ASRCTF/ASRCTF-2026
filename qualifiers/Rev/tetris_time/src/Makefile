CC      = gcc
CFLAGS  = -O2
LDFLAGS = -lncurses
TARGET  = tetris_time
FLAG    = ASRCTF{l3t5_pl4y_s0m3_t3tr15}

BLOB     := $(shell python3 genblob.py '$(FLAG)')
BLOB_LEN := $(shell python3 -c "print(len(b'$(FLAG)'))")

$(TARGET): tetris.c genblob.py
	$(CC) $(CFLAGS) -DFLAG_BYTES='$(BLOB)' -DFLAG_LEN=$(BLOB_LEN) -o $(TARGET) tetris.c $(LDFLAGS)
	strip $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: clean
