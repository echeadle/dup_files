import hashlib
import logging
from typing import Optional

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_CHUNK_SIZE = 8192
SUPPORTED_HASH_ALGORITHMS = ["md5", "sha256"]


def compute_hash(file_path: str, algo: str = "md5") -> Optional[str]:
    """
    Computes the hash of a file using the specified algorithm.

    Args:
        file_path: The path to the file.
        algo: The hashing algorithm to use ("md5" or "sha256").

    Returns:
        The hexadecimal digest of the hash, or None if an error occurs.
    """
    if algo not in SUPPORTED_HASH_ALGORITHMS:
        logger.error(f"Unsupported hashing algorithm: {algo}")
        return None

    try:
        hash_func = hashlib.new(algo)  # Use hashlib.new for dynamic algorithm selection
        with open(file_path, "rb") as f:
            while chunk := f.read(DEFAULT_CHUNK_SIZE):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error hashing {file_path}: {e}")
        return None
