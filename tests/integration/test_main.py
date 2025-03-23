import subprocess
import tempfile
from pathlib import Path
import sys
import os

# Add src to the Python path so we can import from core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# ✅ Now safe to import from core
from core.db_exporter import export_to_csv
from core.report_generator import generate_report



def test_end_to_end_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        db_path = base / "test.db"
        file1 = base / "file1.txt"
        file2 = base / "file2.txt"
        file1.write_text("duplicate")
        file2.write_text("duplicate")

        subprocess.run([
            "python", "src/main.py", str(base), "--db_path", str(db_path)
        ], check=True)

        assert db_path.exists()
        assert db_path.stat().st_size > 0


def test_export_csv_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        db_path = base / "test.db"
        file = base / "file.txt"
        file.write_text("hello world")

        subprocess.run(["python", "src/main.py", str(base), "--db_path", str(db_path)], check=True)

        csv_path = base / "output.csv"
        subprocess.run(["python", "src/main.py", str(base), "--db_path", str(db_path), "--export", str(csv_path)], check=True)

        assert csv_path.exists()
        assert csv_path.read_text().strip() != ""


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
        assert "mp3" in log_path.read_text().lower()


def test_generate_report_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        db_path = base / "test.db"
        file1 = base / "file1.txt"
        file2 = base / "file2.txt"
        file1.write_text("abc123")
        file2.write_text("abc123")

        subprocess.run([
            "python", "src/main.py", str(base), "--db_path", str(db_path)
        ], check=True)

        report_path = base / "report.md"
        subprocess.run([
            "python", "src/main.py", str(base), "--db_path", str(db_path),
            "--report", "--log-file", str(report_path)
        ], check=True)

        assert report_path.exists()
        assert "Duplicate Report" in report_path.read_text()


def test_dry_run_scan():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "file1.txt").write_text("Hello")
        (base / "file2.txt").write_text("World")

        db_path = base / "should_not_exist.db"

        result = subprocess.run([
            "python", "src/main.py", str(base),
            "--db_path", str(db_path),
            "--dry-run"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "Dry run complete" in result.stdout or result.stderr
        assert not db_path.exists()


def test_real_scan_creates_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        file = base / "realfile.txt"
        file.write_text("real content")
        db_path = base / "real.db"

        subprocess.run([
            "python", "src/main.py", str(base), "--db_path", str(db_path)
        ], check=True)

        assert db_path.exists()
        assert db_path.stat().st_size > 0
