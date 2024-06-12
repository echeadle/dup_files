from duplicate_finder import find_duplicates
from output_duplicates import get_duplicates

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", help="Directory to search for duplicate files")
    parser.add_argument("db_path", help="Path to the SQLite database file")
    args = parser.parse_args()

    find_duplicates(args.directory, args.db_path)
    duplicates = get_duplicates(args.db_path)
    for file_hash, paths in duplicates.items():
        print(f"Hash: {file_hash}")
        for path in paths:
            print(f" - {path}")
