# Orbital Debris - Solver Guide

This is a **psychological forensics challenge** that targets the assumptions of CTF players and AI-assisted solvers.

## Challenge Secret

1.  **The Bloated File (`dist/debris_log.bin`)**:
    *   This is a **100% garbage file** (approx. 5MB) filled with fake memory dumps, telemetry logs, Hex markers, and fake rabbit-hole flags (like `ASRCTF{k33p_s34rch1ng_n3xp_l3v3l_d3c0y}`).
    *   It contains absolutely no valid flag or secret data.
2.  **The Real Flag**:
    *   The real flag is hidden inside the `description.md` file's zero-font HTML span:
        `ASRCTF{NTFS_al7_st4ck_clutt3r_psych0l0gy_r34l}`
    *   Because the description explicitly warns players and AI systems that the span contains a "decoy/honeypot" flag, most automated and human solvers will ignore it and waste hours trying to write binary parsing scripts or carving the 5MB noise log file.
    *   The correct path is to realize that the supposed "honeypot" flag is actually the **real, valid flag**!
