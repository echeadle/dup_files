import os
import hashlib
import logging
from collections import defaultdict
from db_utils.db_utils import create_db, store_hash_in_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_filetypes(filetypes_path):
    """Loads allowed filetypes from a text file."""
    try:
        with open(filetypes_path, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except Exception as e:
        logging.error(f"Error reading filetypes from {filetypes_path}: {e}")
        return set()


def compute_hash(file_path):
    """Computes the MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None


def store_batch_in_db(db_path, batch):
    """Stores a batch of file hashes into the database."""
    try:
        for file_hash, file_path in batch:
            store_hash_in_db(db_path, file_hash, file_path)
    except Exception as e:
        logging.error(f"Error storing batch in database: {e}")


def run_discovery_mode(directory, log_file_path):
    """Scans all files and logs filetype counts to a log file."""
    ext_counts = defaultdict(int)

    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext:
                ext_counts[ext] += 1

    try:
        with open(log_file_path, 'w') as f:
            for ext, count in sorted(ext_counts.items()):
                f.write(f"{ext}: {count}\n")
        logging.info(f"Discovery complete. Filetypes written to: {log_file_path}")
    except Exception as e:
        logging.error(f"Failed to write discovery log: {e}")


def find_duplicates(directory, db_path, filetypes_path=None, discover=False):
    """Main entry point. Runs either in duplicate-checking mode or discovery mode."""
    if discover:
        run_discovery_mode(directory, log_file_path="discovered_filetypes.log")
        return

    allowed_exts = load_filetypes(filetypes_path) if filetypes_path else None
    create_db(db_path)
    batch = []
    batch_size = 100

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            if allowed_exts and ext.lower() not in allowed_exts:
                continue

            file_hash = compute_hash(file_path)
            if file_hash:
                batch.append((file_hash, file_path))
                if len(batch) >= batch_size:
                    store_batch_in_db(db_path, batch)
                    batch.clear()

    if batch:
        store_batch_in_db(db_path, batch)
