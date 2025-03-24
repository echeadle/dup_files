import os
import logging
import sqlite3
from typing import List, Tuple, Dict

from core.file_scanner import walk_files, load_filetypes
from core.file_hasher import compute_hash
from db_utils.db_utils import create_db

# --- Constants ---
DEFAULT_BATCH_SIZE = 100
DEFAULT_HASH_ALGO = "md5"

# --- Logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# --- Database Helper Functions ---

def _get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)


def _store_batch_in_db(db_path: str, batch: List[Tuple[str, str]]) -> None:
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


def _get_all_hashes(db_path: str) -> List[str]:
    """Retrieves all unique hashes from the database."""
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM hashes")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving hashes: {e}")
        return []


def _get_paths_for_hash(db_path: str, file_hash: str) -> List[str]:
    """Retrieves all paths associated with a given hash."""
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT path FROM file_paths WHERE hash = ?", (file_hash,)
            )
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving paths for hash {file_hash}: {e}")
        return []


# --- Main Functions ---


def find_duplicates(
    directory: str,
    db_path: str,
    filetypes_path: str = None,
    debug: bool = False,
    batch_size: int = DEFAULT_BATCH_SIZE,
    hash_algo: str = DEFAULT_HASH_ALGO,
) -> Dict[str, int]:
    """Scans a directory, filters by filetypes, and stores hashes and paths in a normalized DB."""
    allowed_exts = (
        load_filetypes(filetypes_path) if filetypes_path else None
    )

    if db_path:
        create_db(db_path)

    scanned = 0
    skipped = 0
    hashed = 0
    batch: List[Tuple[str, str]] = []

    for file_path in walk_files(directory):
        scanned += 1
        _, ext = os.path.splitext(file_path)

        if allowed_exts and ext.lower() not in allowed_exts:
            skipped += 1
            if debug:
                logger.debug(f"[SKIP] {file_path} (filtered by extension)")
            continue

        file_hash = compute_hash(file_path, hash_algo)
        if file_hash:
            batch.append((file_hash, file_path))
            hashed += 1
            if debug:
                logger.debug(f"[HASH] {file_path} → {file_hash}")

        if len(batch) >= batch_size:
            _store_batch_in_db(db_path, batch)
            batch = []

    if batch:
        _store_batch_in_db(db_path, batch)

    logger.info("✅ Scan complete.")
    logger.info(f"  Total scanned: {scanned}")
    logger.info(f"  Skipped (filtered): {skipped}")
    logger.info(f"  Files hashed/stored: {hashed}")

    return {"scanned": scanned, "skipped": skipped, "hashed": hashed}


def print_database_contents(db_path: str) -> None:
    """Prints all hash → path mappings from the normalized database."""
    try:
        hashes = _get_all_hashes(db_path)
        for file_hash in hashes:
            paths = _get_paths_for_hash(db_path, file_hash)
            print(f"\nHash: {file_hash}")
            for path in paths:
                print(f"  ↳ {path}")
    except Exception as e:
        logger.error(f"Error reading database: {e}")


def generate_report(db_path: str) -> None:
    """Generates and prints a human-readable summary of the database."""
    try:
        with _get_db_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM file_paths")
            total_files = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM hashes")
            unique_hashes = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT hash FROM file_paths
                    GROUP BY hash
                    HAVING COUNT(path) > 1
                )
            """
            )
            duplicate_groups = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT MAX(cnt) FROM (
                    SELECT COUNT(path) AS cnt FROM file_paths GROUP BY hash
                )
            """
            )
            max_copies = cursor.fetchone()[0] or 0

            print("\n📊 Duplicate Report")
            print("-" * 30)
            print(f"Total files:         {total_files}")
            print(f"Unique hashes:       {unique_hashes}")
            print(f"Duplicate groups:    {duplicate_groups}")
            print(f"Most copies of one:  {max_copies}")

    except sqlite3.Error as e:
        logger.error(f"Error generating report: {e}")
