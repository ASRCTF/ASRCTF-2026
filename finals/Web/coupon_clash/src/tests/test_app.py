import os
import re
import socket
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

import requests


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


class CouponClashTests(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.database_path = handle.name
        handle.close()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.database_path,
                "SECRET_KEY": "test-secret",
                "REDEEM_DELAY": 0.15,
            }
        )
        with self.app.app_context():
            self.app.init_db()
        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def register(self, username="sprinter", password="race123"):
        return self.client.post(
            "/register",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_single_settlement_is_not_enough_to_buy_flag(self):
        dashboard = self.register()
        coupon_code = re.search(
            rb"Coupon code:</strong>\s*([A-Z0-9-]+)",
            dashboard.data,
        ).group(1).decode("ascii")
        reserve_response = self.client.post(
            "/reserve",
            data={"code": coupon_code},
            follow_redirects=True,
        )
        claim_path = re.search(
            rb'action="(/claim/[^"]+)"',
            reserve_response.data,
        ).group(1).decode("ascii")
        self.client.post(claim_path, follow_redirects=True)
        response = self.client.post("/store/buy/flag", follow_redirects=True)
        self.assertIn(b"Not enough credits yet.", response.data)

    def test_race_redeem_allows_purchase(self):
        port = self.get_free_port()
        server_app = self.app
        server_thread = threading.Thread(
            target=server_app.run,
            kwargs={
                "host": "127.0.0.1",
                "port": port,
                "threaded": True,
                "use_reloader": False,
            },
            daemon=True,
        )
        server_thread.start()
        self.wait_for_server(port)

        base_url = "http://127.0.0.1:{0}".format(port)
        session = requests.Session()
        username = "racer{0}".format(int(time.time()))
        password = "race123"
        register_response = session.post(
            base_url + "/register",
            data={"username": username, "password": password},
            timeout=5,
            allow_redirects=True,
        )
        register_response.raise_for_status()
        coupon_code = re.search(
            r"Coupon code:</strong>\s*([A-Z0-9-]+)",
            register_response.text,
        ).group(1)
        cookies = session.cookies.get_dict()

        session.post(
            base_url + "/reserve",
            data={"code": coupon_code},
            timeout=5,
            allow_redirects=True,
        ).raise_for_status()
        reserve_response = session.get(base_url + "/", timeout=5)
        claim_path = re.search(
            r'action="(/claim/[^"]+)"',
            reserve_response.text,
        ).group(1)
        cookies = session.cookies.get_dict()

        def claim_once():
            return requests.post(
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
        self.assertIn(server_app.config["FLAG"].encode("utf-8"), purchase_response.content)

    @staticmethod
    def get_free_port():
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        listener.close()
        return port

    @staticmethod
    def wait_for_server(port):
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                requests.get("http://127.0.0.1:{0}/".format(port), timeout=0.5)
                return
            except requests.RequestException:
                time.sleep(0.1)
        raise AssertionError("Server did not start in time.")


if __name__ == "__main__":
    unittest.main()
