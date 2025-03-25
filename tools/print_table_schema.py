import sqlite3
import logging
from typing import List

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)


def show_table_schema(db_path: str, table_name: str = "file_paths") -> None:
    """
    Prints the schema of a specified table in an SQLite database.

    Args:
        db_path: The path to the SQLite database file.
        table_name: The name of the table to inspect (default: "file_paths").
    """
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            rows: List[tuple] = cursor.fetchall()
            if not rows:
                logger.warning(f"Table '{table_name}' not found in database.")
                return

            logger.info(f"Schema for table '{table_name}':")
            for row in rows:
                logger.info(row)

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example usage
    show_table_schema("test_hashes.db", "file_paths")