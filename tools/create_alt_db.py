# tools/create_alt_db.py
import sqlite3
import os

db_path = "testdata/alt_test.db"
os.makedirs("testdata", exist_ok=True)

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS file_paths (hash TEXT, path TEXT)")
c.execute("INSERT INTO hashes (hash) VALUES (?)", ("alt123",))
c.execute("INSERT INTO file_paths (hash, path) VALUES (?, ?)", ("alt123", "/new/location/test_file.txt"))
conn.commit()
conn.close()
