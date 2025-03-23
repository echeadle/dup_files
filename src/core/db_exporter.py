import sqlite3
import csv

def export_to_csv(db_path, output_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM hashes")
        hashes = cursor.fetchall()

        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Hash", "File Paths"])

            for (hash_val,) in hashes:
                cursor.execute("SELECT path FROM file_paths WHERE hash = ?", (hash_val,))
                paths = [row[0] for row in cursor.fetchall()]
                writer.writerow([hash_val, ";".join(paths)])

        print(f"[✓] Exported to {output_path}")
    except Exception as e:
        print(f"[!] Export error: {e}")
    finally:
        conn.close()
