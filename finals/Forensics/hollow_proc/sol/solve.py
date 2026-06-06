import re, struct, sys
from pathlib import Path

DATA  = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(__file__).parent.parent / "dist" / "svchost_420.dmp"
MAGIC = b'\xDE\xAD\xC2\xBE'

dump = Path(DATA).read_bytes()

SERVICES_PID = 616
hollow_pid   = None
for line in dump.split(b'\n'):
    m = re.search(rb'svchost\.exe\s+(\d+)\s+(\d+)', line)
    if m:
        pid, ppid = int(m.group(1)), int(m.group(2))
        if ppid != SERVICES_PID:
            hollow_pid = pid
            break

if hollow_pid is None:
    sys.exit(1)

xor_key = hollow_pid & 0xFF

idx = dump.find(MAGIC)
if idx == -1:
    sys.exit(1)

payload_len = struct.unpack('<I', dump[idx + 4:idx + 8])[0]
encoded     = dump[idx + 8:idx + 8 + payload_len]
flag        = bytes(b ^ xor_key for b in encoded).decode()

print(flag)
