weeb_songs_player - Solution

The binary exits immediately under a debugger due to a ptrace anti-debug check.

All UI strings are XOR-encrypted with a rolling key and decrypted at runtime, so nothing useful shows up in strings. A quick dynamic trace recovers the serial prompt and rejection message.

The 16-character serial (XXXX-XXXX-XXXXXX) is split into three parts. Parts 1 and 2 are each hashed via a djb2 variant and compared against two hardcoded 32-bit constants. The [A-Z0-9] alphabet limits each search space to ~1.7M, so you brute-force both in seconds. Multiple collisions exist, but an 8-bit mixing key xk is derived by combining both parts arithmetically; only one (p1, p2) pair produces a valid alphanumeric part 3, giving the serial MP3P-L4YR-5TR34M. The flag is then assembled by XOR-decrypting a masked byte array using the same xk.

Flag: ASRCTF{1_d0nt_533_th3_w33b_50ng5_but_0k}
