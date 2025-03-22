import argparse
import os
import sys

from core.duplicate_handler import (
    find_duplicates,
    print_database_contents,
    export_db_to_csv,
    generate_report
)
from core.discovery import run_discovery_mode

def main():
    parser = argparse.ArgumentParser(description="Duplicate file finder with database, export, discovery, and reporting.")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--db_path", help="Path to SQLite database (required for most actions)")
    parser.add_argument("--filetypes", default="filetypes.txt", help="Path to filetypes list (default: filetypes.txt)")
    parser.add_argument("--discover", action="store_true", help="Run in discovery mode (only logs filetypes)")
    parser.add_argument("--log-file", help="Path to log file for discovery mode (default: discovered_filetypes.log)")
    parser.add_argument("--show-db", action="store_true", help="Print database contents and exit")
    parser.add_argument("--export", help="Export database contents to CSV file")
    parser.add_argument("--report", action="store_true", help="Print a duplicate summary report")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    # Handle CSV export
    if args.export:
        if not args.db_path:
            print("Error: --db_path is required for export.")
            sys.exit(1)
        export_db_to_csv(args.db_path, args.export)
        sys.exit(0)

    # Handle database viewer
    if args.show_db:
        if not args.db_path:
            print("Error: --db_path is required to show database contents.")
            sys.exit(1)
        print_database_contents(args.db_path)
        sys.exit(0)

    # Handle summary report
    if args.report:
        if not args.db_path:
            print("Error: --db_path is required for report.")
            sys.exit(1)
        generate_report(args.db_path)
        sys.exit(0)

    # Handle discovery mode
    if args.discover:
        log_path = args.log_file if args.log_file else "discovered_filetypes.log"
        run_discovery_mode(args.directory, log_file_path=log_path)
        sys.exit(0)

    # Default: scan and deduplicate
    if not args.db_path:
        print("Error: --db_path is required unless --discover is used.")
        sys.exit(1)

    find_duplicates(
        directory=args.directory,
        db_path=args.db_path,
        filetypes_path=args.filetypes,
        debug=args.debug
    )

if __name__ == "__main__":
    main()
