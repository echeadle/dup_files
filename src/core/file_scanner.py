import os
import logging

def load_filetypes(filetypes_path):
    """Loads allowed filetypes from a text file."""
    try:
        with open(filetypes_path, 'r') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except Exception as e:
        logging.error(f"Error reading filetypes from {filetypes_path}: {e}")
        return set()

def walk_files(directory):
    """Yields all file paths within the directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)
