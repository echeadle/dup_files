import sqlite3

def load_duplicates(db_path):
    """Reads duplicates from a normalized DB into a {hash: [paths]} dict."""
    data = {}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT hash FROM hashes")
        hashes = cursor.fetchall()

        for (hash_val,) in hashes:
            cursor.execute("SELECT path FROM file_paths WHERE hash = ?", (hash_val,))
            paths = [row[0] for row in cursor.fetchall()]
            data[hash_val] = paths

        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

    return data
