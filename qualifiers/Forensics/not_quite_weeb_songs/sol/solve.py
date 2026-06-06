import base64, json, sys
from datetime import datetime, timezone
from pathlib import Path

DATA  = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(__file__).parent.parent / "dist" / "Streaming_History_Audio_2026.json"
MAGIC = 1337

def ts(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

records = json.loads(Path(DATA).read_text())

# Step 1: find IP hop gap -> XOR key
xor_key = None
for i in range(1, len(records)):
    a, b = records[i-1], records[i]
    if a["ip_addr_decrypted"] == b["ip_addr_decrypted"]: continue
    gap = (ts(b["ts"]) - ts(a["ts"])).total_seconds()
    if 0 < gap < 600:
        xor_key = int(gap)
        break

# Step 2: find rollback session, decode payload
rollback_idx = next(i for i in range(1, len(records)) if ts(records[i]["ts"]) < ts(records[i-1]["ts"]))
ip = records[rollback_idx]["ip_addr_decrypted"]
start = next(i for i in range(rollback_idx, -1, -1) if records[i]["ip_addr_decrypted"] != ip) + 1
end   = next((i for i in range(rollback_idx, len(records)) if records[i]["ip_addr_decrypted"] != ip), len(records))
session = records[start:end]

b64_str = "".join(chr((r["ms_played"] // MAGIC) ^ xor_key) for r in session)
flag    = base64.b64decode(b64_str).decode()

print(f"XOR key : {xor_key}")
print(f"Base64  : {b64_str}")
print(f"Flag    : {flag}")
