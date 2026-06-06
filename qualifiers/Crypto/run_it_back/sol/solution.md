run_it_back - Solution

The cipher computes encrypt(s)[i] = (11·s[i−1] + 7·s[i+1] + KEY[i]) mod 37 over the 37-character alphabet. A fixed point requires s[i] = 11·s[i−1] + 7·s[i+1] + KEY[i] for all i, giving the linear system (I − C)·s = KEY mod 37, where C is the circulant matrix encoding the two neighbour weights. Since 37 is prime and I − C has full rank, the system has a unique solution, recoverable by Gaussian elimination mod 37.

Flag: `ASRCTF{y0u_5p1n_m3_r1ght_r0und}`
