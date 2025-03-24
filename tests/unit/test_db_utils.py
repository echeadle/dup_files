import os
import sqlite3
import tempfile
import sys

# Add src/ to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from db_utils.db_utils import create_db, store_hash_in_db

def test_create_and_store_hash_and_path():
    with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        create_db(db_path)

        test_hash = "abc123"
        test_path = "/some/file.txt"

        store_hash_in_db(db_path, test_hash, test_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if hash exists
        cursor.execute("SELECT hash FROM hashes WHERE hash=?", (test_hash,))
        assert cursor.fetchone()[0] == test_hash

        # Check if path is linked to hash
        cursor.execute("SELECT path FROM file_paths WHERE hash=?", (test_hash,))
        result = cursor.fetchall()
        paths = [row[0] for row in result]

        assert test_path in paths
        assert len(paths) == 1  # Only one path expected

        conn.close()
    finally:
        os.remove(db_path)


def test_duplicate_path_not_inserted_twice():
    with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        create_db(db_path)

        test_hash = "dup456"
        test_path = "/another/file.txt"

        # Insert same path twice for same hash
        store_hash_in_db(db_path, test_hash, test_path)
        store_hash_in_db(db_path, test_hash, test_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Confirm only one row exists for that hash/path combo
        cursor.execute("SELECT COUNT(*) FROM file_paths WHERE hash=? AND path=?", (test_hash, test_path))
        count = cursor.fetchone()[0]

        assert count == 1, f"Expected 1 path entry, got {count}"

        conn.close()
    finally:
        os.remove(db_path)
