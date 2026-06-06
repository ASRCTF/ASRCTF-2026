Nebula Signal - Solution

The flag is encoded across the pixels of deep_field_NGC7293.png using four steganographic methods in rotation. For each pixel index i, the encoding method is determined by i mod 4:

  i mod 4 == 0  ->  bit stored in LSB of red channel
  i mod 4 == 1  ->  bit stored in LSB of blue channel
  i mod 4 == 2  ->  bit stored in LSB of green channel
  i mod 4 == 3  ->  bit stored as parity of (R + G + B)

A four-byte null sequence marks the end of the message.

```bash
python3 solve.py deep_field_NGC7293.png
```

Running the program gives you the flag:
Flag: ASRCTF{y0u_c4n_d0_c00l_th1ngs_w1th_l5b5}
