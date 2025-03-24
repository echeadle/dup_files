import os
import logging
from collections import defaultdict
from core.file_scanner import walk_files

def run_discovery_mode(directory, log_file_path):
    """Scans all files and logs filetype counts to a log file."""
    ext_counts = defaultdict(int)

    for file_path in walk_files(directory):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext:
            ext_counts[ext] += 1

    try:
        with open(log_file_path, 'w') as f:
            for ext, count in sorted(ext_counts.items()):
                f.write(f"{ext}: {count}\n")
        logging.info(f"Discovery complete. Filetypes written to: {log_file_path}")
    except Exception as e:
        logging.error(f"Failed to write discovery log: {e}")
