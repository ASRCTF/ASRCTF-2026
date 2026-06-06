import re, struct, sys, base64
import Evtx.Evtx as evtx_mod
import Evtx.Views as V

PATH = sys.argv[1] if len(sys.argv) > 1 else 'dist/ground_ctrl_ps.evtx'
print(f"[*] Opening: {PATH}")

part1_chars = []
part2 = None

with evtx_mod.Evtx(PATH) as log:
    for chunk in log.chunks():
        recs = sorted(chunk.records(), key=lambda r: r.record_num())
        for rec in recs:
            ft = struct.unpack_from('<Q', rec._buf, rec._offset + 16)[0]
            part1_chars.append((ft % 10_000_000) // 10_000)

        for rec in recs:
            m = re.search(r"FromBase64String\('([A-Za-z0-9+/=]+)'\)",
                          V.evtx_record_xml_view(rec))
            if m:
                part2 = base64.b64decode(m.group(1)).decode()
                print(f"Record {rec.record_num()} base64 → {part2!r}")

part1 = bytes(part1_chars).decode('ascii')
print(f"Timestamps ms  → {part1!r}")

flag = part1 + part2
print(f"FLAG: {flag}")
