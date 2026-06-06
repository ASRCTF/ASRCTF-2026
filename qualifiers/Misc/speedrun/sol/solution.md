Speedrun - Solution

The file is a valid iNES-format NES ROM. Running strings or a hex dump reveals a hint buried in the PRG-ROM at offset 0x110: an input sequence 0,0,1,1,2,3,2,3,4,5 (the Konami code, controller-indexed) and a tile mapping function. The CHR-ROM section starts at byte 16 + prg_size and holds 512 tiles of 16 bytes each. For each flag character at position i, the tile index is (i*37 + seq[i%10]*13 + 7) % 512, and the first byte of that tile holds its ASCII value. Running solve.py extracts all 45 characters directly.

Flag: `ASRCTF{up_up_d0wn_d0wn_l3ft_r1ght_l3ft_r1ght}`
