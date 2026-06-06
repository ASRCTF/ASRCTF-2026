TON-618 - Solution

clock/ holds 80 empty files whose mtimes encode a path, one bit per file: read each mtime mod 2, reassemble 8-bit groups MSB-first to get bin/oracle.

The binary takes a 20-bit integer mask, checks whether the corresponding subset of twenty hard-coded 10-digit integers sums to a fixed target, and prints the flag if it does. Solve it with meet-in-the-middle: split the 20 elements into two halves, enumerate all 1024 subset sums for each, then scan for a complementary pair. Feed the recovered mask to the binary.

Flag: ASRCTF{why_15_th3_r3v_50_fr33}
