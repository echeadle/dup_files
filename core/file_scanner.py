import logging
from pathlib import Path
from typing import Set, Optional, Generator


# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_filetypes(filetypes_path: str) -> Set[str]:
    """Loads allowed filetypes from a text file."""
    try:
        with open(filetypes_path, "r") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        logger.error(f"File not found: {filetypes_path}")
        return set()
    except Exception as e:
        logger.error(f"Error reading filetypes from {filetypes_path}: {e}")
        return set()

def load_excluded_dirs(excluded_path: str) -> Set[str]:
    """Loads directory names to exclude from a text file. Returns an empty set if the file is not found or empty."""
    try:
        with open(excluded_path, "r") as f:
            return {line.strip() for line in f if line.strip()} # Use set comprehension
    except FileNotFoundError:
        logger.warning(f"Exclusions file not found: {excluded_path}. No directories excluded.") # Changed to warning
        return set()
    except Exception as e:
        logger.error(f"Error loading exclusions from {excluded_path}: {e}")
        return set()



def walk_files(
    directory: str,
    included_filetypes: Optional[Set[str]] = None,
    excluded_dirs: Optional[Set[str]] = None,
    debug: bool = False,
) -> Generator[str, None, None]:
    """
    Recursively walk through directory and yield matching file paths.

    Args:
        directory: The directory to walk through.
        included_filetypes: Set of extensions (e.g. {'.txt', '.jpg'}).
        excluded_dirs: Set of directory names to skip.
        debug: If True, log skipped files.

    Yields:
        File paths that match the criteria.
    """
    directory = Path(directory)
    scanned = 0
    yielded = 0

    for entry in directory.rglob("*"):
        scanned += 1

        # Skip entries if any part of the path is in the excluded_dirs set
        if excluded_dirs and any(part in excluded_dirs for part in entry.parts):
            if debug:
                logger.debug(f"[EXCLUDED] {entry}")
            continue  # <--- This line and the following code were not indented

        if entry.is_file():
            if included_filetypes and entry.suffix.lower() not in included_filetypes:
                if debug:
                    logger.debug(f"[EXT-SKIP] {entry}")
                continue

            yielded += 1
            yield str(entry)

    logger.info(f"Walked {scanned} entries, yielded {yielded} matching files")

