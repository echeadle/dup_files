import os
import logging
from pathlib import Path



import logging

def load_filetypes(filetypes_path):
    """Loads allowed filetypes from a text file."""
    try:
        with open(filetypes_path, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except Exception as e:
        logging.error(f"Error reading filetypes from {filetypes_path}: {e}")
        return set()


def load_excluded_dirs(excluded_path):
    """Loads directory names to exclude from a text file."""
    try:
        with open(excluded_path, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        logging.error(f"Error reading excluded dirs from {excluded_path}: {e}")
        return set()

def walk_files(directory, included_filetypes=None, excluded_dirs=None, debug=False):
    """
    Recursively walk through directory and yield matching file paths.
    - included_filetypes: set of extensions (e.g. {'.txt', '.jpg'})
    - excluded_dirs: set of directory names to skip
    - debug: if True, log skipped files
    """
    directory = Path(directory)
    scanned = 0
    yielded = 0

    for entry in directory.rglob("*"):
        scanned += 1

        if entry.is_dir():
            if excluded_dirs and entry.name in excluded_dirs:
                if debug:
                    logging.debug(f"[DIR-SKIP] {entry}")
                continue

        elif entry.is_file():
            if included_filetypes and entry.suffix.lower() not in included_filetypes:
                if debug:
                    logging.debug(f"[EXT-SKIP] {entry}")
                continue

            yielded += 1
            yield str(entry)

    logging.info(f"Walked {scanned} entries, yielded {yielded} matching files")


