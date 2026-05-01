import os
import tempfile
import unittest

from database import get_db, init_db


class DatabaseTests(unittest.TestCase):
    def test_init_db_creates_required_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "app.db")
            init_db(db_path)

            conn = get_db(db_path)
            tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            conn.close()

            self.assertGreaterEqual(tables, {"users", "tasks", "login_attempts"})
