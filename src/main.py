import argparse
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

from core.duplicate_handler import (
    find_duplicates,
    print_database_contents
)
from core.discovery import run_discovery_mode
from core.report_generator import generate_report
from core.db_exporter import export_to_csv 


load_dotenv()  # Load variables from .env if available

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Duplicate File Finder")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--db_path", help="Path to the SQLite database")
    parser.add_argument("--filetypes", help="Filetypes config path")
    parser.add_argument("--exclude", help="Exclusions config path")
    parser.add_argument("--discover", action="store_true", help="Run discovery mode")
    parser.add_argument("--show-db", action="store_true", help="Print DB contents")
    parser.add_argument("--export", help="Export DB to CSV at given path")
    parser.add_argument("--report", action="store_true", help="Generate report of duplicates")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without saving to DB")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--log-file", help="Write report output to file instead of stdout")
    parser.add_argument("--hash-algo", choices=["md5", "sha256"], default="md5",
                        help="Hashing algorithm to use (default: md5)")

    args = parser.parse_args()

    # Allow default DB path from .env if not passed
    db_path = args.db_path or os.getenv("DEFAULT_DB_PATH")

    if args.discover:
        log_path = args.log_file or "discovered_filetypes.log"
        run_discovery_mode(args.directory, log_path)
        return

    if args.show_db:
        print_database_contents(db_path)
        return

    if args.export:
        export_to_csv(db_path, args.export)
        return

    if args.report:
        report = generate_report(db_path)
        if args.log_file:
            with open(args.log_file, "w") as f:
                f.write(report)
        else:
            print(report)
        return

    # Log hashing algorithm being used
    logger.info(f"Using hash algorithm: {args.hash_algo.upper()}")

    # Actual duplicate detection
    results = find_duplicates(
        args.directory,
        db_path=None if args.dry_run else db_path,
        filetypes_path=args.filetypes,
        debug=args.debug,
        hash_algo=args.hash_algo
    )

    logger.info("✅ Scan complete.")
    logger.info(f"  Total scanned: {results['scanned']}")
    logger.info(f"  Skipped (filtered): {results['skipped']}")
    logger.info(f"  Files hashed/stored: {results['hashed']}")

    if args.dry_run:
        logger.info("Dry run complete. No changes saved.")

if __name__ == "__main__":
    main()
