Very Bad Accounting - Solution

Each cell in column F of the Ouroboros sheet holds a self-referential formula
=F{n}/2 + {k}/2, where k is the ASCII codepoint of a flag character. Without
iterative calculation enabled the sheet errors out entirely. Enabling it in
LibreOffice lets each cell converge to its codepoint, so you can chr() each rounded value to read the flag.

```bash
pip install openpyxl
python3 solve.py
```

Flag: `ASRCTF{c1rcul4r_r3f3r3nc1ng_15_qu1t3_4_pr0bl3m}`
