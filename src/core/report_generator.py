import sqlite3

def generate_report(db_path):
    """Generates and returns a human-readable summary of duplicates."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT hash, GROUP_CONCAT(path, '; ') FROM file_paths
            GROUP BY hash HAVING COUNT(path) > 1
        """)
        duplicates = cursor.fetchall()

        report_lines = ["📊 Duplicate Report", "=" * 50]
        for hash_val, paths in duplicates:
            report_lines.append(f"\nHash: {hash_val}")
            for path in paths.split("; "):
                report_lines.append(f"  - {path}")
        
        conn.close()
        return "\n".join(report_lines)
    except Exception as e:
        print(f"Error generating report: {e}")
        return None

