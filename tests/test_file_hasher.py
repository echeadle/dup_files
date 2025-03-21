import tempfile
import os
from core.file_hasher import compute_hash

def test_compute_hash_on_known_content():
    content = b"Hello, hash me!"
    expected_hash = "56c3bd26ac7013161dd75af7b92ba75d"  # Precomputed MD5

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        result = compute_hash(tmp_file_path)
        assert result == expected_hash, f"Expected {expected_hash}, got {result}"
    finally:
        os.remove(tmp_file_path)
