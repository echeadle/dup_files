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
