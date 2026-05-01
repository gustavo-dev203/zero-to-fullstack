import os
import tempfile
import unittest
from unittest.mock import patch

from auth import (
    authenticate_user,
    get_login_block_message,
    is_login_allowed,
    register_user,
    validate_email,
    validate_name,
)
from database import get_db, init_db


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "auth.db")
        init_db(self.db_path)
        self.db = get_db(self.db_path)

    def tearDown(self):
        self.db.close()
        self.tempdir.cleanup()

    @patch("auth.has_valid_email_domain", return_value=True)
    def test_validate_email_accepts_valid_address(self, _):
        self.assertTrue(validate_email("usuario@example.com"))

    def test_validate_name_rejects_short_values(self):
        self.assertFalse(validate_name("x"))
        self.assertTrue(validate_name("Nome válido"))

    @patch("auth.has_valid_email_domain", return_value=True)
    def test_register_user_and_authentication(self, _):
        self.assertTrue(register_user(self.db, "Teste", "usuario@example.com", "SenhaSegura1"))

        user = authenticate_user(self.db, "usuario@example.com", "SenhaSegura1")
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "usuario@example.com")

    @patch("auth.has_valid_email_domain", return_value=False)
    def test_register_user_rejects_invalid_email_domain(self, _):
        self.assertFalse(register_user(self.db, "Teste", "usuario@invalid-domain", "SenhaSegura1"))

    @patch("auth.has_valid_email_domain", return_value=True)
    def test_login_lockout_after_failed_attempts(self, _):
        self.assertTrue(register_user(self.db, "Teste", "usuario@example.com", "SenhaSegura1"))

        for _ in range(5):
            self.assertIsNone(authenticate_user(self.db, "usuario@example.com", "senhaerrada"))

        self.assertFalse(is_login_allowed(self.db, "usuario@example.com"))
        message = get_login_block_message(self.db, "usuario@example.com")
        self.assertIsNotNone(message)
        self.assertIn("bloqueada temporariamente", message.lower())
