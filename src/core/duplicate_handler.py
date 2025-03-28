import os
import logging
import sqlite3

from core.file_scanner import walk_files, load_filetypes
from core.file_hasher import compute_hash
from db_utils.db_utils import create_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def store_batch_in_db(db_path, batch):
    """Stores a batch of (hash, path) pairs into the database."""
    if not db_path:
        logger.warning("No database path provided. Skipping batch insert.")
        return

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        for file_hash, file_path in batch:
            c.execute('INSERT OR IGNORE INTO hashes (hash) VALUES (?)', (file_hash,))
            c.execute('SELECT 1 FROM file_paths WHERE hash = ? AND path = ?', (file_hash, file_path))
            if not c.fetchone():
                c.execute('INSERT INTO file_paths (hash, path) VALUES (?, ?)', (file_hash, file_path))

        conn.commit()
        logger.info(f"✅ Stored batch of {len(batch)} entries in DB.")
    except Exception as e:
        logger.error(f"❌ Error in batch insert: {e}")
    finally:
        conn.close()


def find_duplicates(directory, db_path, filetypes_path=None, debug=False, batch_size=100, hash_algo="md5"):
    """Scans a directory, filters by filetypes, and stores hashes and paths in normalized DB."""
    allowed_exts = load_filetypes(filetypes_path) if filetypes_path else None

    if db_path:
        create_db(db_path)

    scanned = 0
    skipped = 0
    hashed = 0
    batch = []

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
            store_batch_in_db(db_path, batch)
            batch = []

    if batch:
        store_batch_in_db(db_path, batch)

    logger.info("✅ Scan complete.")
    logger.info(f"  Total scanned: {scanned}")
    logger.info(f"  Skipped (filtered): {skipped}")
    logger.info(f"  Files hashed/stored: {hashed}")

    return {
        "scanned": scanned,
        "skipped": skipped,
        "hashed": hashed
    }


def print_database_contents(db_path):
    """Prints all hash → path mappings from the normalized database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT hash FROM hashes")
        hashes = cursor.fetchall()

        for (hash_val,) in hashes:
            cursor.execute("SELECT path FROM file_paths WHERE hash = ?", (hash_val,))
            paths = cursor.fetchall()

            print(f"\nHash: {hash_val}")
            for (path,) in paths:
                print(f"  ↳ {path}")

        conn.close()
    except Exception as e:
        logger.error(f"Error reading database: {e}")


def generate_report(db_path):
    """Generates and prints a human-readable summary of the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM file_paths")
        total_files = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM hashes")
        unique_hashes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT hash FROM file_paths
                GROUP BY hash
                HAVING COUNT(path) > 1
            )
        """)
        duplicate_groups = cursor.fetchone()[0]

        cursor.execute("""
            SELECT MAX(cnt) FROM (
                SELECT COUNT(path) AS cnt FROM file_paths GROUP BY hash
            )
        """)
        max_copies = cursor.fetchone()[0] or 0

        print("\n📊 Duplicate Report")
        print("-" * 30)
        print(f"Total files:         {total_files}")
        print(f"Unique hashes:       {unique_hashes}")
        print(f"Duplicate groups:    {duplicate_groups}")
        print(f"Most copies of one:  {max_copies}")

        conn.close()
    except Exception as e:
        logger.error(f"Error generating report: {e}")
