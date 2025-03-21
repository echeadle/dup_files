import os
import sqlite3
import tempfile
import sys

# Add src/ to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from db_utils.db_utils import create_db, store_hash_in_db

def test_create_and_store_in_db():
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        # Step 1: Create the database
        create_db(db_path)

        # Step 2: Insert a known hash/path
        test_hash = "abc123"
        test_path = "/some/file/path.txt"
        store_hash_in_db(db_path, test_hash, test_path)

        # Step 3: Verify it's in the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash, paths FROM file_hashes WHERE hash=?", (test_hash,))
        result = cursor.fetchone()
        conn.close()

        assert result == (test_hash, test_path), f"Expected ({test_hash}, {test_path}), got {result}"

    finally:
        os.remove(db_path)


def test_duplicate_paths_append_to_db():
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        create_db(db_path)

        test_hash = "dup123"
        path1 = "/file/a.txt"
        path2 = "/file/b.txt"

        store_hash_in_db(db_path, test_hash, path1)
        store_hash_in_db(db_path, test_hash, path2)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT paths FROM file_hashes WHERE hash=?", (test_hash,))
        result = cursor.fetchone()[0]
        conn.close()

        # Convert semicolon-separated paths to list
        path_list = [p.strip() for p in result.split(";")]

        assert path1 in path_list, f"{path1} missing from {path_list}"
        assert path2 in path_list, f"{path2} missing from {path_list}"
        assert len(path_list) == 2, f"Expected 2 paths, got: {path_list}"

    finally:
        os.remove(db_path)
