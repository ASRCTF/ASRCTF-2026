Duck Hunt - Solution

The flag is hidden inside a deleted PDF file on a FAT12 disk image. The
deletion leaves the directory entry and file data intact on disk; only the
FAT chain is zeroed and the first byte of the entry is overwritten with
0xE5. The PDF contains two comment lines in its raw byte stream that are
invisible to any viewer. Together they encode the flag across three
transformations applied in sequence.

  Step 1  ->  locate and carve the deleted PDF from the raw disk image
  Step 2  ->  extract the Base64 payload and shifted key from PDF comments
  Step 3  ->  undo the Caesar shift on the key (n = -7) to recover the hex byte
  Step 4  ->  XOR each decoded Base64 byte against the key to recover the flag

```bash
python3 solve.py yata_disk.img
```

Running the program gives you the flag:
Flag: ASRCTF{c4n_w3_st1ll_unl04d_th3_duck5_pl3453}
