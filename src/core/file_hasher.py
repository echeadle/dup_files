import hashlib
import logging

logger = logging.getLogger(__name__)

def compute_hash(file_path, algo="md5"):
    """
    Compute the hash of a file using the specified algorithm.

    Args:
        file_path (str or Path): Path to the file.
        algo (str): Hash algorithm to use. Options: 'md5', 'sha256'.

    Returns:
        str: Hex digest of the file's hash, or None on failure.
    """
    hash_func = hashlib.md5() if algo == "md5" else hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash {file_path} using {algo.upper()}: {e}")
        return None
