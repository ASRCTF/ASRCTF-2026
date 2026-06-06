import http.server
import importlib.util
import sys
from pathlib import Path

SRC  = Path(__file__).parent
DIST = SRC.parent / "dist"

HOST = "localhost"
PORT = 8080


def run(script: str):
    path = SRC / script
    spec = importlib.util.spec_from_file_location(script, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build()


class Handler(http.server.BaseHTTPRequestHandler):
    SERVED = {"capture_47.pcap", "vault_3c8f.db", "fs_shard.dd", "coredump.bin"}

    def do_GET(self):
        name = self.path.lstrip("/")
        if name not in self.SERVED:
            self.send_error(404)
            return
        f = DIST / name
        if not f.exists():
            self.send_error(404)
            return
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")


if __name__ == "__main__":
    for script in [
        "build_layer1_pcap.py",
        "build_layer2_sqlite.py",
        "build_layer3_ext2.py",
        "build_layer4_coredump.py",
    ]:
        try:
            run(script)
        except Exception as exc:
            print(f"ERROR in {script}: {exc}", file=sys.stderr)
            sys.exit(1)

    print(f"Serving on http://{HOST}:{PORT}/capture_47.pcap")
    http.server.HTTPServer((HOST, PORT), Handler).serve_forever()
