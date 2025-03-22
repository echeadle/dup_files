import os
import sqlite3
import tempfile
import subprocess
from pathlib import Path

def test_end_to_end_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        file1 = base / "a.txt"
        file2 = base / "b.txt"
        file3 = base / "unique.txt"
        db_path = base / "test.db"

        # Two identical files
        file1.write_text("duplicate content")
        file2.write_text("duplicate content")
        file3.write_text("unique content")

        # Run the CLI tool
        subprocess.run([
            "python", "src/main.py", str(base),
            "--db_path", str(db_path)
        ], check=True)

        # Connect to DB and validate results
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM hashes")
        unique_hashes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT hash FROM file_paths
                GROUP BY hash
                HAVING COUNT(path) > 1
            )
        """)
        duplicate_groups = cursor.fetchone()[0]

        conn.close()

        assert unique_hashes == 2
        assert duplicate_groups == 1
import csv

def test_export_csv_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        db_path = base / "test.db"
        file = base / "file.txt"
        file.write_text("hello world")

        subprocess.run(["python", "src/main.py", str(base), "--db_path", str(db_path)], check=True)

        csv_path = base / "output.csv"
        subprocess.run(["python", "src/main.py", str(base), "--db_path", str(db_path), "--export", str(csv_path)], check=True)

        with open(csv_path) as f:
            reader = list(csv.reader(f))
            assert reader[0] == ["hash", "path"]
            assert len(reader) == 2

def test_discovery_logs_types():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "test.mp3").write_bytes(b"audio")
        (base / "another.doc").write_bytes(b"doc")
        log_path = base / "custom_discovery.log"

        subprocess.run([
            "python", "src/main.py", str(base),
            "--discover",
            "--log-file", str(log_path)
        ], check=True)

        assert log_path.exists()
        content = log_path.read_text()
        assert ".mp3" in content
        assert ".doc" in content

def test_generate_report_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        file1 = base / "d1.txt"
        file2 = base / "d2.txt"
        file1.write_text("dup")
        file2.write_text("dup")
        db_path = base / "test.db"

        subprocess.run(["python", "src/main.py", str(base), "--db_path", str(db_path)], check=True)

        # Capture report output
        result = subprocess.run(
            ["python", "src/main.py", str(base), "--db_path", str(db_path), "--report"],
            check=True,
            capture_output=True,
            text=True
        )

        assert "Duplicate Report" in result.stdout
        assert "Duplicate groups:" in result.stdout


if __name__ == "__main__":
    test_end_to_end_duplicate_detection()