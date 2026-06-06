import random
from pathlib import Path
from scapy.all import wrpcap
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP

OUT = Path(__file__).parent.parent / "dist" / "capture_47.pcap"

NOISE_DOMAINS = [
    "www.microsoft.com", "windowsupdate.com", "ocsp.digicert.com",
    "ctldl.windowsupdate.com", "settings-win.data.microsoft.com",
    "time.windows.com", "login.microsoftonline.com",
    "dc.services.visualstudio.com", "www.google.com",
    "safebrowsing.googleapis.com", "clients1.google.com",
    "update.googleapis.com", "accounts.google.com",
    "teredo.ipv6.microsoft.com",
]

CLIENT  = "10.0.0.47"
GATEWAY = "10.0.0.1"


def _query(qname, sport, ts):
    pkt = IP(src=CLIENT, dst=GATEWAY, ttl=64) / UDP(sport=sport, dport=53) / \
          DNS(id=random.randint(0x0800, 0xEFFF), rd=1, qd=DNSQR(qname=qname, qtype="A"))
    pkt.time = ts
    return pkt


def _response(qname, sport, ts, rdata="93.184.216.34"):
    pkt = IP(src=GATEWAY, dst=CLIENT, ttl=128) / UDP(sport=53, dport=sport) / \
          DNS(id=random.randint(0x0800, 0xEFFF), qr=1, aa=1, rd=1, ra=1,
              qd=DNSQR(qname=qname, qtype="A"),
              an=DNSRR(rrname=qname, type="A", rdata=rdata, ttl=300))
    pkt.time = ts + 0.022
    return pkt


def _nxdomain(qname, sport, ts):
    pkt = IP(src=GATEWAY, dst=CLIENT, ttl=128) / UDP(sport=53, dport=sport) / \
          DNS(id=random.randint(0x0800, 0xEFFF), qr=1, rd=1, ra=1, rcode=3,
              qd=DNSQR(qname=qname, qtype="A"))
    pkt.time = ts + 0.019
    return pkt


def build(seed: int = 0xDEAD):
    random.seed(seed)
    packets = []
    base_ts = 1_710_000_000.0
    sport   = 49_152

    for i, domain in enumerate(NOISE_DOMAINS):
        ts = base_ts + i * 4.7 + random.uniform(0.0, 0.8)
        sp = sport + i
        q  = domain + "."
        packets.append(_query(q, sp, ts))
        packets.append(_response(q, sp, ts))

    filename = b"vault_3c8f.db"
    hexstr   = filename.hex()
    chunks   = [hexstr[i:i+4] for i in range(0, len(hexstr), 4)]
    burst_ts = base_ts + 68.0

    for j, chunk in enumerate(chunks):
        label = f"{chunk}.seq{j:02d}.sync.corp-fileserver.internal."
        sp    = sport + 200 + j
        ts    = burst_ts + j * 0.31 + random.uniform(0.0, 0.04)
        packets.append(_query(label, sp, ts))
        packets.append(_nxdomain(label, sp, ts))

    for i, domain in enumerate(NOISE_DOMAINS):
        ts = base_ts + 150.0 + i * 3.2 + random.uniform(0.0, 0.5)
        sp = sport + 300 + i
        q  = domain + "."
        packets.append(_query(q, sp, ts))
        packets.append(_response(q, sp, ts))

    packets.sort(key=lambda p: p.time)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(OUT), packets)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build()
