import os
import hashlib
import logging
from db_utils import create_db, store_hash_in_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compute_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None

def find_duplicates(directory, db_path):
    create_db(db_path)
    batch_size = 100
    batch = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = compute_hash(file_path)
            if file_hash:
                batch.append((file_hash, file_path))
                if len(batch) >= batch_size:
                    store_batch_in_db(db_path, batch)
                    batch.clear()

    if batch:
        store_batch_in_db(db_path, batch)

def store_batch_in_db(db_path, batch):
    try:
        for file_hash, file_path in batch:
            store_hash_in_db(db_path, file_hash, file_path)
    except Exception as e:
        logging.error(f"Error storing batch in database: {e}")

if __name__ == "__main__":
    directory = "/path/to/directory"
    db_path = "/path/to/database.db"
    find_duplicates(directory, db_path)
