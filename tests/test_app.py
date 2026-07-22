import sqlite3
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit_app


class EstateDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db_path = Path(__file__).parent / "test_estate_command_center.db"
        if self.db_path.exists():
            self.db_path.unlink()

    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()

    def test_schema_migration_adds_deed_fingerprint_column(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "CREATE TABLE properties (id INTEGER PRIMARY KEY AUTOINCREMENT, property_name TEXT NOT NULL, owner_name TEXT, deed_data TEXT)"
        )
        conn.execute("INSERT INTO properties (property_name, owner_name, deed_data) VALUES (?, ?, ?)", ("123 Main", "Jane Doe", "sample deed"))
        conn.commit()
        conn.close()

        streamlit_app.ensure_database_schema(self.db_path)

        conn = sqlite3.connect(self.db_path)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(properties)")]
        self.assertIn("deed_fingerprint", columns)

        streamlit_app.add_property(self.db_path, "456 Oak", "John Smith", "deed text", "abc123")
        rows = streamlit_app.get_properties(self.db_path)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["property_name"], "456 Oak")
        self.assertEqual(rows[1]["deed_fingerprint"], "abc123")
        conn.close()


if __name__ == "__main__":
    unittest.main()
