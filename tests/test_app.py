import os
import tempfile
import unittest
from unittest.mock import patch

from app import app
from database import init_db


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "app.db")
        init_db(self.db_path)

        app.config["DATABASE_PATH"] = self.db_path
        app.config["TESTING"] = True
        app.secret_key = "test-secret"
        self.client = app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_index_redirects_to_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    @patch("auth.has_valid_email_domain", return_value=True)
    def test_register_and_login_flow(self, _):
        with self.client as client:
            with client.session_transaction() as sess:
                sess["csrf_token"] = "test-token"

            response = client.post(
                "/register",
                data={
                    "name": "Teste",
                    "email": "usuario@example.com",
                    "password": "SenhaSegura1",
                    "password_confirm": "SenhaSegura1",
                    "csrf_token": "test-token",
                },
                follow_redirects=False,
            )
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers["Location"])

            with client.session_transaction() as sess:
                sess["csrf_token"] = "test-token"

            response = client.post(
                "/login",
                data={
                    "email": "usuario@example.com",
                    "password": "SenhaSegura1",
                    "csrf_token": "test-token",
                },
                follow_redirects=False,
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers["Location"].endswith("/"))

    def test_post_without_csrf_is_rejected(self):
        response = self.client.post("/login", data={"email": "a@b.com", "password": "x"})
        self.assertEqual(response.status_code, 400)
