import sqlite3
from pathlib import Path

OUT       = Path(__file__).parent.parent / "dist" / "vault_3c8f.db"
AES_KEY   = "b7e3a914c6f82d053f9a1b7c4e8d2f60"
NEXT_FILE = "fs_shard.dd"


def _fill_page(cursor, page_size: int = 4096) -> None:
    n = (page_size * 2) // 130 + 4
    for i in range(n):
        cursor.execute("INSERT INTO _pad VALUES (?,?)", (i, "PADDINGROW_" + "Z" * 100))


def build():
    if OUT.exists():
        OUT.unlink()

    conn = sqlite3.connect(str(OUT))
    conn.execute("PRAGMA page_size = 4096")
    conn.execute("PRAGMA journal_mode = DELETE")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE ops_log (
            id        INTEGER PRIMARY KEY,
            timestamp TEXT    NOT NULL,
            operator  TEXT    NOT NULL,
            action    TEXT    NOT NULL,
            detail    TEXT,
            status    TEXT    NOT NULL
        )
    """)
    c.executemany("INSERT INTO ops_log VALUES (?,?,?,?,?,?)", [
        (1,  "2024-03-09 01:12:04", "svc_backup",    "BACKUP_START",    "Volume: C:\\",                         "OK"),
        (2,  "2024-03-09 01:14:47", "svc_backup",    "BACKUP_COMPLETE", "Snapshot: snap_20240309_011204",        "OK"),
        (3,  "2024-03-09 02:00:01", "svc_monitor",   "HEARTBEAT",       "cpu=12 mem=34",                        "OK"),
        (4,  "2024-03-09 02:30:01", "svc_monitor",   "HEARTBEAT",       "cpu=9 mem=35",                         "OK"),
        (5,  "2024-03-09 03:00:01", "svc_monitor",   "HEARTBEAT",       "cpu=11 mem=34",                        "OK"),
        (6,  "2024-03-09 03:05:18", "op_harrington", "LOGIN",           "src=10.0.0.22",                        "OK"),
        (7,  "2024-03-09 03:07:33", "op_harrington", "FILE_ACCESS",     "path=D:\\ops\\schedule.xlsx",          "OK"),
        (8,  "2024-03-09 03:08:55", "op_harrington", "FILE_ACCESS",     "path=D:\\ops\\roster_q1.xlsx",         "OK"),
        (9,  "2024-03-09 03:09:11", "op_harrington", "FILE_ACCESS",     "path=D:\\ops\\contingency_alpha.docx", "OK"),
        (10, "2024-03-09 03:11:55", "op_harrington", "LOGOUT",          "",                                     "OK"),
        (11, "2024-03-09 03:14:02", "svc_monitor",   "ALERT",           "anomalous_pid=420 parent=cmd.exe",     "WARN"),
        (12, "2024-03-09 03:14:07", "svc_edr",       "QUARANTINE",      "target=svchost.exe pid=420",           "OK"),
        (13, "2024-03-09 03:30:01", "svc_monitor",   "HEARTBEAT",       "cpu=8 mem=33",                         "OK"),
        (14, "2024-03-09 04:00:01", "svc_monitor",   "HEARTBEAT",       "cpu=10 mem=33",                        "OK"),
        (15, "2024-03-09 04:01:44", "svc_backup",    "BACKUP_START",    "Volume: D:\\",                         "OK"),
        (16, "2024-03-09 04:04:22", "svc_backup",    "BACKUP_COMPLETE", "Snapshot: snap_20240309_040144",       "OK"),
    ])

    c.execute("CREATE TABLE system_config (key TEXT PRIMARY KEY, value TEXT)")
    c.executemany("INSERT INTO system_config VALUES (?,?)", [
        ("hostname",       "WORKSTATION-7F2A"),
        ("os_version",     "Windows 10 Pro 22H2"),
        ("edr_version",    "SentinelOne 23.4.1"),
        ("log_retention",  "90"),
        ("backup_dest",    "\\\\NAS01\\backups\\"),
        ("encryption_key", "PLACEHOLDER_NOT_THE_KEY"),
    ])
    conn.commit()

    c.execute("CREATE TABLE _pad (id INTEGER PRIMARY KEY, data TEXT)")
    _fill_page(c)
    conn.commit()

    c.execute("INSERT INTO ops_log VALUES (?,?,?,?,?,?)",
              (99, "2024-03-09 03:13:58", "op_mercer", "EXFIL_STAGE",
               f"key={AES_KEY} next={NEXT_FILE}", "PURGED"))
    conn.commit()
    c.execute("DELETE FROM ops_log WHERE id = 99")
    conn.commit()
    conn.close()

    raw = OUT.read_bytes()
    if not (AES_KEY.encode() in raw and NEXT_FILE.encode() in raw):
        slack = (
            b"\x00" * 16
            + b"DELETED_RECORD\x00"
            + f"op_mercer\x002024-03-09 03:13:58\x00EXFIL_STAGE\x00"
              f"key={AES_KEY} next={NEXT_FILE}\x00PURGED\x00".encode()
            + b"\x00" * 16
        )
        with OUT.open("ab") as f:
            f.write(slack)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build()
