import os
import logging
import sqlite3

from core.file_scanner import walk_files, load_filetypes
from core.file_hasher import compute_hash
from db_utils.db_utils import create_dbimport os
import logging
import sqlite3

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
, store_hash_in_db

def store_batch_in_db(db_path, batch):
    """Stores a batch of file hashes into the database."""
    try:
        for file_hash, file_path in batch:
            store_hash_in_db(db_path, file_hash, file_path)
    except Exception as e:
        logging.error(f"Error storing batch in database: {e}")

def find_duplicates(directory, db_path, filetypes_path=None):
    """Scans a directory, filters by filetypes, and stores hashes and paths in normalized DB."""
    allowed_exts = load_filetypes(filetypes_path) if filetypes_path else None
    create_db(db_path)

    for file_path in walk_files(directory):
        print(f"Checking: {file_path}")  # 🔍 DEBUG LINE

        _, ext = os.path.splitext(file_path)
        if allowed_exts:
            print(f"Allowed extensions: {allowed_exts}")  # 🔍 DEBUG
            print(f"File extension: {ext.lower()}")       # 🔍 DEBUG

        if allowed_exts and ext.lower() not in allowed_exts:
            print(f"Skipping {file_path} (not in allowed_exts)")  # 🔍 DEBUG
            continue

        file_hash = compute_hash(file_path)
        if file_hash:
            print(f"Hash: {file_hash}")  # 🔍 DEBUG
            store_hash_in_db(db_path, file_hash, file_path)

def print_database_contents(db_path):
    """Prints all hash → path mappings from the normalized database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all hashes
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
