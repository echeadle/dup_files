import argparse
from duplicate_finder import find_duplicates

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", help="Directory to scan for duplicates")
    parser.add_argument("db_path", help="Path to SQLite database file")
    args = parser.parse_args()

    find_duplicates(args.directory, args.db_path)

if __name__ == "__main__":
    main()
