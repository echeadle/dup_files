import os
import hashlib
from db_utils import create_db, store_hash_in_db

def compute_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def find_duplicates(directory, db_path):
    create_db(db_path)
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = compute_hash(file_path)
            store_hash_in_db(db_path, file_hash, file_path)
