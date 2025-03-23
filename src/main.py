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
    generate_report,
    export_duplicates_to_csv,
)

def main():
    parser = argparse.ArgumentParser(description="Duplicate File Finder CLI")

    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--db_path", default="hashes.db", help="Path to SQLite database")
    parser.add_argument("--filetypes", help="Path to file with allowed extensions")
    parser.add_argument("--exclude", help="Path to file with excluded directories")
    parser.add_argument("--discover", action="store_true", help="Log all discovered filetypes")
    parser.add_argument("--log-file", help="Path to discovery log file (used with --discover)")
    parser.add_argument("--export", help="Export duplicates to CSV file")
    parser.add_argument("--show-db", action="store_true", help="Print all database entries")
    parser.add_argument("--report", action="store_true", help="Print summary report to stdout")
    parser.add_argument("--dry-run", action="store_true", help="Simulate scan without writing to database")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    filetypes_path = args.filetypes or "config/included_filetypes.txt"
    included_exts = load_filetypes(filetypes_path)

    excluded_path = args.exclude or "config/excluded_dirs.txt"
    excluded_dirs = load_excluded_dirs(excluded_path)

    if args.discover:
        discovered = set()
        for file_path in walk_files(args.directory, excluded_dirs=excluded_dirs, debug=args.debug):
            _, ext = os.path.splitext(file_path)
            if ext:
                discovered.add(ext.lower())

        out_path = args.log_file or "discovered_filetypes.log"
        with open(out_path, "w") as f:
            for ext in sorted(discovered):
                f.write(f"{ext}\n")
        logging.info(f"Discovered {len(discovered)} file types written to {out_path}")
        return

    if args.show_db:
        print_database_contents(args.db_path)
        return

    if args.report:
        generate_report(args.db_path)
        return

    if args.export:
        export_duplicates_to_csv(args.db_path, args.export)
        logging.info(f"Export complete: {args.export}")
        return

    if args.dry_run:
        logging.info("⚠️ Dry run mode — no DB will be written.")
    else:
        create_db(args.db_path)

    scanned, hashed, skipped = 0, 0, 0
    batch = []

    logging.info("Starting duplicate scan...")

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
    logging.info(f"  Skipped: {skipped}")

    if args.dry_run:
        logging.info("✅ Dry run complete.")

if __name__ == "__main__":
    main()
