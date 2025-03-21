import sqlite3

def create_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create hashes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS hashes (
            hash TEXT PRIMARY KEY
        )
    ''')

    # Create file_paths table
    c.execute('''
        CREATE TABLE IF NOT EXISTS file_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT,
            path TEXT,
            FOREIGN KEY (hash) REFERENCES hashes(hash)
        )
    ''')

    conn.commit()
    conn.close()


def store_hash_in_db(db_path, file_hash, file_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Step 1: Insert hash if it doesn't exist
    c.execute('INSERT OR IGNORE INTO hashes (hash) VALUES (?)', (file_hash,))

    # Step 2: Check if this path for the hash already exists
    c.execute('SELECT 1 FROM file_paths WHERE hash = ? AND path = ?', (file_hash, file_path))
    exists = c.fetchone()

    if not exists:
        # Step 3: Insert the path for this hash
        c.execute('INSERT INTO file_paths (hash, path) VALUES (?, ?)', (file_hash, file_path))

    conn.commit()
    conn.close()
