import sqlite3
import csv
import logging
from pathlib import Path
from typing import List

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)


def _get_paths_for_hash(conn: sqlite3.Connection, file_hash: str) -> List[str]:
    """Retrieves all paths associated with a given hash."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT path FROM file_paths WHERE hash = ?", (file_hash,)
    )
    return [row[0] for row in cursor.fetchall()]


def export_to_csv(db_path: Path, output_path: Path) -> None:
    """Exports the contents of the database to a CSV file.

    Args:
        db_path: The path to the SQLite database file.
        output_path: The path to the output CSV file.
    """
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM hashes")
            hashes = cursor.fetchall()

            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Hash", "File Paths"])

                for (hash_val,) in hashes:
                    paths = _get_paths_for_hash(conn, hash_val)
                    writer.writerow([hash_val, ";".join(paths)])

            logger.info(f"✅ Exported to {output_path}")
    except sqlite3.Error as e:
        logger.error(f"❌ Export error: {e}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")

