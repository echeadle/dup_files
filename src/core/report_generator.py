import sqlite3

def generate_report(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM hashes")
        hashes = cursor.fetchall()

        print("📊 Duplicate Report")
        print("=" * 50)
        for (hash_val,) in hashes:
            cursor.execute("SELECT path FROM file_paths WHERE hash = ?", (hash_val,))
            paths = [row[0] for row in cursor.fetchall()]
            if len(paths) > 1:
                print(f"\nHash: {hash_val}")
                for path in paths:
                    print(f"  - {path}")

        print("\nReport generation complete.")
    except Exception as e:
        print(f"[!] Report error: {e}")
    finally:
        conn.close()
