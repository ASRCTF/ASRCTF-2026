from http.server import BaseHTTPRequestHandler, HTTPServer

HTML = b"""<!DOCTYPE html>
<html>
<head><title>NEXUS Portal</title></head>
<body>
<h1>NEXUS Internal Portal</h1>
<p>Status: <strong>OPERATIONAL</strong></p>
<p>Nothing to see here. Move along.</p>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("X-Secret-Token", "ng_th3")
        self.send_header("Server", "NEXUS/2.1.0")
        self.end_headers()
        self.wfile.write(HTML)

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    HTTPServer((<host>, <port>), Handler).serve_forever()
