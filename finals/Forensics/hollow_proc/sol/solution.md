hollow_proc - Solution

The flag is hidden inside a fabricated Windows memory dump. Two anomalies
chain together: the first identifies the hollowed process and yields an XOR
key; the second locates a custom C2 frame in the injected shellcode and
decodes the payload.

  Step 1  ->  parse the embedded process list; spot the svchost.exe
              whose parent is cmd.exe (PID 3120) instead of services.exe
              (PID 616) -> anomalous process is PID 420
  Step 2  ->  inspect the VAD snapshot for PID 420; the main image region
              0x400000-0x401fff carries PAGE_EXECUTE_READWRITE instead of
              the PAGE_EXECUTE_READ a legitimately loaded PE would have,
              confirming the region was written after the original image
              was unmapped (classic process hollowing)
  Step 3  ->  derive the XOR key: key = PID & 0xFF = 420 & 0xFF = 0xA4 (164)
              the injected shellcode corroborates this: a `mov eax, 0x1A4`
              instruction encodes the PID before the XOR decode loop
  Step 4  ->  scan the dump for the C2 magic bytes DE AD C2 BE; the four
              bytes that follow are a little-endian payload length; XOR
              each payload byte with 0xA4 to recover the flag

```bash
python3 solve.py svchost_420.dmp
```

Running the solver gives you the flag:
Flag: ASRCTF{n33dl3_1n_th3_m3m0ry_dump}
