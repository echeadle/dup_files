import hashlib
import logging

# Setup logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def compute_hash(file_path, algo="md5"):
    """
    Compute the hash of a file using the specified algorithm (md5 or sha256).
    Returns the hex digest string or None on failure.
    """
    try:
        if algo == "md5":
            hash_func = hashlib.md5()
        elif algo == "sha256":
            hash_func = hashlib.sha256()
        else:
            logger.error(f"Unsupported hashing algorithm: {algo}")
            return None

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    except Exception as e:
        logger.error(f"Error hashing {file_path}: {e}")
        return None
