import sqlite3

def get_duplicates(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM file_hashes')
    duplicates = {row[0]: row[1].split(';') for row in c.fetchall() if len(row[1].split(';')) > 1}
    conn.close()
    return duplicates
