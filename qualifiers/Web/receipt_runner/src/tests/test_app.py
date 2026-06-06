import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


class ReceiptRunnerTests(unittest.TestCase):
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

    def register(self, username="player1", password="pass123"):
        return self.client.post(
            "/register",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_dashboard_lists_only_owned_receipt(self):
        response = self.register()
        self.assertIn(b"Welcome Pack", response.data)
        self.assertNotIn(b"Organizer Reimbursement", response.data)

    def test_public_receipt_route_checks_ownership(self):
        self.register()
        response = self.client.get("/receipts/8421")
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_organizer_access_returns_401(self):
        self.register()
        blocked = self.client.get("/organizer/receipts/8421")
        self.assertEqual(blocked.status_code, 401)


if __name__ == "__main__":
    unittest.main()
