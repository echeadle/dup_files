import os
import logging
from core.file_scanner import walk_files, load_filetypes
from core.file_hasher import compute_hash
from db_utils.db_utils import create_db, store_hash_in_db

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
        _, ext = os.path.splitext(file_path)
        if allowed_exts and ext.lower() not in allowed_exts:
            continue

        file_hash = compute_hash(file_path)
        if file_hash:
            store_hash_in_db(db_path, file_hash, file_path)
