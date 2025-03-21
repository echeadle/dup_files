import argparse
from src.duplicate_finder import find_duplicates
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Duplicate file finder with discovery mode and filetype filtering.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--db_path", help="Path to SQLite database (required unless --discover is used)")
    parser.add_argument("--filetypes", default="filetypes.txt", help="Path to filetypes list (default: filetypes.txt)")
    parser.add_argument("--discover", action="store_true", help="Run in discovery mode (only logs filetypes)")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    if not args.discover and not args.db_path:
        print("Error: --db_path is required unless --discover is used.")
        sys.exit(1)

    find_duplicates(
        directory=args.directory,
        db_path=args.db_path,
        filetypes_path=args.filetypes,
        discover=args.discover
    )

if __name__ == "__main__":
    main()
