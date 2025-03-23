import argparse
import os
import logging

from core.file_scanner import (
    walk_files,
    load_filetypes,
    load_excluded_dirs,
)
from core.file_hasher import compute_hash
from core.duplicate_handler import (
    create_db,
    store_batch_in_db,
    print_database_contents,
    generate_report
)
def main():
    parser = argparse.ArgumentParser(description="Duplicate File Finder")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--db_path", help="Path to SQLite database", default="hashes.db")
    parser.add_argument("--filetypes", help="Path to file with included file extensions (one per line)")
    parser.add_argument("--exclude", help="Path to file with directory names to exclude")
    parser.add_argument("--discover", action="store_true", help="Log all file types found (no hashing or DB storage)")
    parser.add_argument("--show-db", action="store_true", help="Print contents of the database")
    parser.add_argument("--report", action="store_true", help="Print report of duplicates")
    parser.add_argument("--dry-run", action="store_true", help="Simulate scan without writing to the database")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Load included filetypes
    filetypes_path = args.filetypes or "config/included_filetypes.txt"
    included_exts = load_filetypes(filetypes_path)
    if included_exts:
        logging.info(f"Including file extensions: {', '.join(sorted(included_exts))}")
    else:
        logging.info("No filetype filtering applied.")

    # Load excluded directories
    excluded_path = args.exclude or "config/excluded_dirs.txt"
    excluded_dirs = load_excluded_dirs(excluded_path)
    if excluded_dirs:
        logging.info(f"Excluding directories: {', '.join(sorted(excluded_dirs))}")

    # DISCOVERY MODE
    if args.discover:
        discovered = set()
        for file_path in walk_files(args.directory, excluded_dirs=excluded_dirs, debug=args.debug):
            _, ext = os.path.splitext(file_path)
            if ext:
                discovered.add(ext.lower())
        with open("discovered_filetypes.log", "w") as log:
            for ext in sorted(discovered):
                log.write(f"{ext}\n")
        logging.info(f"Discovered {len(discovered)} file types written to discovered_filetypes.log")
        return

    # SHOW DATABASE CONTENTS
    if args.show_db:
        print_database_contents(args.db_path)
        return

    # REPORT MODE
    if args.report:
        generate_report(args.db_path)
        return

    # DRY RUN MODE
    if args.dry_run:
        logging.info("⚠️ Dry run mode enabled — database will NOT be created or written to.")

    else:
        # Initialize database
        create_db(args.db_path)

    # FILE SCANNING & HASHING
    logging.info("Starting duplicate scan...")

    batch = []
    scanned = 0
    hashed = 0
    skipped = 0

    for file_path in walk_files(args.directory, included_exts, excluded_dirs, debug=args.debug):
        scanned += 1
        file_hash = compute_hash(file_path)
        if file_hash:
            hashed += 1
            batch.append((file_hash, file_path))
            if len(batch) >= 100 and not args.dry_run:
                store_batch_in_db(args.db_path, batch)
                batch = []
        else:
            skipped += 1

    if batch and not args.dry_run:
        store_batch_in_db(args.db_path, batch)

    logging.info("Scan complete.")
    logging.info(f"  Scanned: {scanned}")
    logging.info(f"  Hashed: {hashed}")
    logging.info(f"  Skipped (no hash or error): {skipped}")

    if args.dry_run:
        logging.info("✅ Dry run complete — no changes were written to the database.")


if __name__ == "__main__":
    main()
