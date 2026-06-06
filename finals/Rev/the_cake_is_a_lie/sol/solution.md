The Cake Is A Lie - Solution

The binary CRC32-guards an XOR-encrypted Verilog netlist in .rodata; patching the integrity check causes an immediate abort. Disassembly reveals the blob key (0xA3) as an immediate in the decrypt loop. Decrypting the blob yields a 128-bit post-synthesis netlist, but the pass/invert pattern encodes a masked target, not the raw secret: a second XOR mask is applied to the input in main before calling bake_unit. Extracting the mask from the two ULL immediates and XORing against the target bits recovers "Candleeggssweets".

Flag: ASRCTF{but_th3_b1n4ry_n3v3r_l135}
