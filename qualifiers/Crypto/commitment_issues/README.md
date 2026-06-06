Set the flag via environment variable and expose with `ncat`:

```bash
FLAG="ASRCTF{pr1m35_4r3_qu1t3_1ntr1gu1ng}" ncat -lkp <port> -e python3 server.py
```
Also, change the host and port in chall.py and description.
