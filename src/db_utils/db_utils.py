import sqlite3
import logging
from typing import List, Tuple

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)


def create_db(db_path: str) -> None:
    """Creates the database and necessary tables if they don't exist."""
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS hashes (
                    hash TEXT PRIMARY KEY
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS file_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT,
                    path TEXT,
                    FOREIGN KEY (hash) REFERENCES hashes(hash)
                )
                """
            )
            conn.commit()
            logger.info(f"✅ Database created/verified at {db_path}")
    except sqlite3.Error as e:
        logger.error(f"❌ Error creating database: {e}")


def store_hash_in_db(db_path: str, file_hash: str, file_path: str) -> None:
    """Stores a file hash and its path in the database."""
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            # Insert hash if it doesn't exist
            cursor.execute(
                "INSERT OR IGNORE INTO hashes (hash) VALUES (?)", (file_hash,)
            )

            # Check if the path for this hash already exists
            cursor.execute(
                "SELECT 1 FROM file_paths WHERE hash = ? AND path = ?",
                (file_hash, file_path),
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    "INSERT INTO file_paths (hash, path) VALUES (?, ?)",
                    (file_hash, file_path),
                )
                logger.debug(f"➕ Stored hash: {file_hash}, path: {file_path}")

            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"❌ Error storing hash: {e}")

def store_batch_in_db(db_path: str, batch: List[Tuple[str, str]]) -> None:
    """Stores a batch of (hash, path) pairs into the database."""
    if not db_path:
        logger.warning("No database path provided. Skipping batch insert.")
        return

    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            for file_hash, file_path in batch:
                cursor.execute(
                    "INSERT OR IGNORE INTO hashes (hash) VALUES (?)", (file_hash,)
                )
                cursor.execute(
                    "SELECT 1 FROM file_paths WHERE hash = ? AND path = ?",
                    (file_hash, file_path),
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO file_paths (hash, path) VALUES (?, ?)",
                        (file_hash, file_path),
                    )
            conn.commit()
            logger.info(f"✅ Stored batch of {len(batch)} entries in DB.")
    except sqlite3.Error as e:
        logger.error(f"❌ Error in batch insert: {e}")
