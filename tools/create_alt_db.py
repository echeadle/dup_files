# tools/create_alt_db.py
import sqlite3
import os

db_path = "testdata/alt_test.db"
os.makedirs("testdata", exist_ok=True)

# tools/create_alt_db.py
import sqlite3
import os
import logging
from pathlib import Path

# --- Constants ---
DB_DIR = Path("testdata")
DB_NAME = "alt_test.db"
DB_PATH = DB_DIR / DB_NAME
TEST_HASH = "alt123"
TEST_PATH = "/new/location/test_file.txt"

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)


def create_alt_db(db_path: Path, test_hash: str, test_path: str) -> None:
    """Creates an alternative test database with predefined data."""
    try:
        DB_DIR.mkdir(exist_ok=True)  # Ensure the directory exists
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS file_paths (hash TEXT, path TEXT)"
            )

            cursor.execute("INSERT INTO hashes (hash) VALUES (?)", (test_hash,))
            cursor.execute(
                "INSERT INTO file_paths (hash, path) VALUES (?, ?)",
                (test_hash, test_path),
            )

            conn.commit()
            logger.info(f"✅ Alternative database created at: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"❌ Error creating alternative database: {e}")


if __name__ == "__main__":
    create_alt_db(DB_PATH, TEST_HASH, TEST_PATH)
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS file_paths (hash TEXT, path TEXT)")
c.execute("INSERT INTO hashes (hash) VALUES (?)", ("alt123",))
c.execute("INSERT INTO file_paths (hash, path) VALUES (?, ?)", ("alt123", "/new/location/test_file.txt"))
conn.commit()
conn.close()
