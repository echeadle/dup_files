import sqlite3
import logging
from typing import Optional
from db.db_utils import _get_db_connection

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def generate_report(db_path: str) -> Optional[str]:
    """
    Generates and returns a human-readable summary of duplicate files.

    Args:
        db_path: The path to the SQLite database file.

    Returns:
        A string containing the report, or None if an error occurs.
    """
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT hash, GROUP_CONCAT(path, '; ')
                FROM file_paths
                GROUP BY hash
                HAVING COUNT(path) > 1
                """
            )
            duplicates = cursor.fetchall()

            report_lines = ["📊 Duplicate Report", "=" * 50]
            for hash_val, paths in duplicates:
                report_lines.append(f"\nHash: {hash_val}")
                for path in paths.split("; "):
                    report_lines.append(f"  - {path}")

            return "\n".join(report_lines)

    except sqlite3.Error as e:
        logger.error(f"Database error generating report: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
