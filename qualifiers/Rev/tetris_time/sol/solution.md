tetris_time - Solution

The flag is concealed inside a stripped ELF binary through a dual-condition
gate. Decompiling main() and update_score() reveals two boolean flags,
cond_tetris_l3 and cond_keybind_l4, both of which must be set before
reveal_flag() is called.

Condition A is set inside update_score() when exactly 4 lines are cleared
(a Tetris) and the level at the time of the clear was 3. Level is captured
before lines_total is incremented, so the window is lines 30–39.

Condition B is set in the 'f' key-press branch of the input handler when
level == 4 (lines 40–49). The key does not appear in the on-screen controls.

reveal_flag() derives a 29-byte keystream from a Galois 16-bit LFSR (seed
0xACE1, tap mask 0xB400) and XORs it against the encrypted blob in .rodata
to recover the flag, which it prints to the terminal.

```bash
python3 solve.py tetris_time
```

Flag: ASRCTF{l3t5_pl4y_s0m3_t3tr15}
