import sqlite3

def show_table_schema(db_path, table_name="file_hashes"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    for row in cursor.fetchall():
        print(row)
    conn.close()

# Example usage
show_table_schema("file_hashes.db")
