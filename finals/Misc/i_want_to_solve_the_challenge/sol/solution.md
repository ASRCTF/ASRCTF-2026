I Want To Solve The Challenge - Solution

The puzzle is pure HTTP exploration. The root response headers hint toward robots.txt,
which discloses a hidden path. That path returns a base64-encoded body decoding to a
knock sequence. POSTing the correct sequence to /knock unlocks /finally, which returns
the flag XOR'd against a random key supplied in the X-Key response header.

Flag: `ASRCTF{th3_ch4ll3ng3_w3r3_th3_fr13nd5_w3_m4d3_4l0ng_th3_w4y}`
