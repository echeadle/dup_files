import os
import logging
import sqlite3
import csv
from core.file_scanner import walk_files, load_filetypes
from core.file_hasher import compute_hash
from db_utils.db_utils import create_db, store_hash_in_db

def store_batch_in_db(db_path, batch):
    """Stores a batch of (hash, path) pairs into the database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        for file_hash, file_path in batch:
            # Insert hash if not already present
            c.execute('INSERT OR IGNORE INTO hashes (hash) VALUES (?)', (file_hash,))
            # Avoid duplicate paths
            c.execute('SELECT 1 FROM file_paths WHERE hash = ? AND path = ?', (file_hash, file_path))
            if not c.fetchone():
                c.execute('INSERT INTO file_paths (hash, path) VALUES (?, ?)', (file_hash, file_path))
        conn.commit()
    except Exception as e:
        print(f"Error in batch insert: {e}")
    finally:
        conn.close()

def find_duplicates(directory, db_path, filetypes_path=None, debug=False, batch_size=100):
    """Scans a directory, filters by filetypes, and stores hashes and paths in normalized DB."""
    allowed_exts = load_filetypes(filetypes_path) if filetypes_path else None
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
                print(f"[SKIP] {file_path} (filtered out by extension)")
            continue

        file_hash = compute_hash(file_path)
        if file_hash:
            batch.append((file_hash, file_path))
            hashed += 1
            if debug:
                print(f"[HASH] {file_path} → {file_hash}")

        if len(batch) >= batch_size:
            store_batch_in_db(db_path, batch)
            batch = []

    if batch:
        store_batch_in_db(db_path, batch)

    print(f"\nScan complete.")
    print(f"  Total scanned: {scanned}")
    print(f"  Skipped (filtered): {skipped}")
    print(f"  Files hashed/stored: {hashed}")

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
        print(f"Error reading database: {e}")


def generate_report(db_path):
    """Generates and prints a human-readable summary of the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Total file paths
        cursor.execute("SELECT COUNT(*) FROM file_paths")
        total_files = cursor.fetchone()[0]

        # Unique hashes
        cursor.execute("SELECT COUNT(*) FROM hashes")
        unique_hashes = cursor.fetchone()[0]

        # Duplicate groups (hashes with more than 1 path)
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT hash FROM file_paths
                GROUP BY hash
                HAVING COUNT(path) > 1
            )
        """)
        duplicate_groups = cursor.fetchone()[0]

        # Max number of copies for any one hash
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
        print(f"Error generating report: {e}")

