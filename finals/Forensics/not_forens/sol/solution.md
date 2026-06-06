not_forens - Solution

The flag is buried four layers deep. Only capture_47.pcap is distributed;
every subsequent filename must be recovered by solving the previous layer.

  capture_47.pcap  ->  vault_3c8f.db  ->  fs_shard.dd  ->  coredump.bin  ->  FLAG
       PCAP              SQLite            ext2/AES           ELF core
   DNS labelling       raw byte          inode slack         PT_NOTE +
     pattern           forensics           space             XOR decode

Layer 1 — capture_47.pcap

Filter for DNS. Among routine Windows resolver noise, a burst of 14
packets queries *.sync.corp-fileserver.internal with all NXDOMAIN
responses. Each FQDN follows the pattern:

    <hex>.seq<NN>.sync.corp-fileserver.internal

Sort by the seq## counter, concatenate the hex labels, and hex-decode:

    7661 756c 745f 3363 3866 2e64 62
    -> 7661756c745f336338662e6462
    -> "vault_3c8f.db"

Layer 2 — vault_3c8f.db

Two tables: ops_log (16 rows) and system_config. The encryption_key
field in system_config is a red herring. A row was inserted into ops_log
and deleted without VACUUM; SQLite does not zero freed slot bytes, so the
deleted record survives in the raw file. Run strings or scan for "key=":

    strings vault_3c8f.db | grep "key="

The deleted row (operator: op_mercer, action: EXFIL_STAGE) contains:

    key=b7e3a914c6f82d053f9a1b7c4e8d2f60 next=fs_shard.dd

Layer 3 — fs_shard.dd

this is an AES-128-CBC encrypted blob. The first
16 bytes are the IV; the remainder is the ciphertext of a raw ext2 image.
Decrypt with the key from layer 2, then mount or use debugfs:

    /ops/transfer_log.txt  ->  inode reports i_size = 40
                               allocated block is 1024 bytes

The 984 bytes beyond i_size are invisible to the OS but present on disk.
Read the raw block (e.g. debugfs dump_inode) to recover the slack:

    xor_key=CAFED00D next=coredump.bin

Layer 4 — coredump.bin

An ELF ET_CORE file with three program headers: one PT_NOTE and two
PT_LOAD segments. The PT_NOTE contains an NT_FILE entry that maps
0xDEAD0000-0xDEAD1000 to "[dead_drop_payload]": a name that does not
correspond to any real library or binary. That vaddr matches the second
PT_LOAD segment. Extract its 256 bytes and XOR-decode with the 4-byte
repeating key 0xCAFED00D from layer 3:

    python3 solve.py dist/

Flag: ASRCTF{50m3_m0r3_l3v3l5_w0uld_b3_n1ce}
