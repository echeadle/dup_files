import os
import hashlib
import sqlite3

def create_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS file_hashes (
            hash TEXT PRIMARY KEY,
            paths TEXT
        )
    ''')
    conn.commit()
    conn.close()

def compute_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def store_hash_in_db(db_path, file_hash, file_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT paths FROM file_hashes WHERE hash = ?', (file_hash,))
    row = c.fetchone()
    if row:
        paths = row[0].split(';')
        if file_path not in paths:
            paths.append(file_path)
            c.execute('UPDATE file_hashes SET paths = ? WHERE hash = ?', (';'.join(paths), file_hash))
    else:
        c.execute('INSERT INTO file_hashes (hash, paths) VALUES (?, ?)', (file_hash, file_path))
    conn.commit()
    conn.close()

def find_duplicates(directory, db_path):
    create_db(db_path)
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = compute_hash(file_path)
            store_hash_in_db(db_path, file_hash, file_path)

def get_duplicates(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM file_hashes')
    duplicates = {row[0]: row[1].split(';') for row in c.fetchall() if len(row[1].split(';')) > 1}
    conn.close()
    return duplicates

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", help="Directory to search for duplicate files")
    parser.add_argument("db_path", help="Path to the SQLite database file")
    args = parser.parse_args()

    find_duplicates(args.directory, args.db_path)
    duplicates = get_duplicates(args.db_path)
    for file_hash, paths in duplicates.items():
        print(f"Hash: {file_hash}")
        for path in paths:
            print(f" - {path}")
