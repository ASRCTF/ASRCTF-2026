import os
import socket
import sys
import threading
import time
import unittest

import requests


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


class LoopbackLoungeTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_literal_localhost_is_blocked(self):
        self.assertTrue(self.app.is_blocked_target("http://localhost:5000/internal/flag"))
        response = self.client.get("/?path=http://localhost:5000/internal/flag")
        self.assertIn(b"blocked by policy", response.data)

    def test_absolute_path_ignores_sponsor_base_url(self):
        target = self.app.build_preview_target("http://[::1]:5001/internal/flag")
        self.assertEqual(target, "http://[::1]:5001/internal/flag")
        self.assertFalse(self.app.is_blocked_target(target))

    def test_internal_flag_requires_loopback(self):
        forbidden = self.client.get(
            "/internal/flag",
            environ_overrides={"REMOTE_ADDR": "8.8.8.8"},
        )
        allowed = self.client.get(
            "/internal/flag",
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(allowed.status_code, 200)
        self.assertIn(self.app.config["FLAG"].encode("utf-8"), allowed.data)

    def test_preview_can_reach_numeric_loopback(self):
        port = self.get_free_port()
        internal_port = self.get_free_port()
        self.app.config["INTERNAL_PORT"] = internal_port
        self.app.start_internal_server()
        server_thread = threading.Thread(
            target=self.app.run,
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

        response = requests.get(
            "http://127.0.0.1:{0}/".format(port),
            params={"path": "http://[::1]:{0}/internal/flag".format(internal_port)},
            timeout=5,
        )
        response.raise_for_status()
        self.assertIn(self.app.config["FLAG"], response.text)

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
