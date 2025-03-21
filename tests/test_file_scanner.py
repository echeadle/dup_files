import tempfile
import os
import sys
import pytest

# Ensure src/ is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.file_scanner import load_filetypes, walk_files

def test_load_filetypes_from_file():
    content = ".jpg\n.mp4\n.PDF\n"
    expected = {".jpg", ".mp4", ".pdf"}

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        result = load_filetypes(tmp_file_path)
        assert result == expected, f"Expected {expected}, got {result}"
    finally:
        os.remove(tmp_file_path)

def test_walk_files_yields_all_files(tmp_path):
    # Create a nested test directory
    (tmp_path / "subdir").mkdir()
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "subdir" / "file2.txt"
    file1.write_text("hello")
    file2.write_text("world")

    found = set(walk_files(tmp_path))

    assert str(file1) in found
    assert str(file2) in found

