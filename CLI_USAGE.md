# 🧰 CLI Usage Guide — Duplicate Files Tool

This guide outlines how to use the command-line interface (CLI) provided by `src/main.py` to scan for duplicate files, log file types, and generate reports.

---

## 🔧 Basic Command

```
python src/main.py <directory> [options]
```

Where `<directory>` is the path you want to scan.

---

## ✅ Available CLI Options

| Option             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `--db_path`        | Path to the SQLite database file to use or create                          |
| `--filetypes`      | Path to a `.txt` file listing allowed file extensions (one per line)       |
| `--discover`       | Discovery mode: logs all encountered file types (no hashing or DB storage) |
| `--show-db`        | Displays the current contents of the database in the console               |
| `--report`         | Prints a report of all hashes and associated file paths                    |

---

## 📌 Usage Examples

### 1. 🔍 Scan a folder for duplicates and save to DB

```
python src/main.py ~/Downloads --db_path mydata.db
```

Stores all file hashes and paths to `mydata.db`.

---

### 2. 🧪 Discovery mode (list all file extensions found)

```
python src/main.py ~/Documents --discover
```

Generates a file: `discovered_filetypes.log` with one file extension per line.

---

### 3. 🎯 Filter scan to certain file types

```
python src/main.py ~/Photos --filetypes config/filetypes.txt
```

Only hashes files that match the extensions listed in `filetypes.txt`.

---

### 4. 📂 Show database contents

```
python src/main.py . --db_path mydata.db --show-db
```

Prints all `hash → path` entries from the DB.

---

### 5. 🧾 Generate a summary report

```
python src/main.py my_data --db_path mydata.db --report
```

Outputs a readable report:

```
Hash: 6d3a12...
  ↳ /some/path/file1.txt
  ↳ /backup/file1_copy.txt
```

---

## 📦 Log Files

| File                         | Description                                 |
|------------------------------|---------------------------------------------|
| `discovered_filetypes.log`   | Created during `--discover` mode            |
| `exported/exported.log`      | Files exported via web interface            |
| `exported/deleted.log`       | Files deleted via web interface             |

---

## 🧠 Tips

- Use `--discover` first to see what file types exist in a folder.
- Then build a `filetypes.txt` list and use `--filetypes` to refine scanning.
- Combine with `--report` to review duplicates before taking action.

---

## 🧪 Example Workflow

```
# Step 1: Log file types
python src/main.py ~/Media --discover

# Step 2: Create filetypes.txt (e.g. .mp4, .mov)

# Step 3: Scan with filters and store results
python src/main.py ~/Media --filetypes filetypes.txt --db_path media.db

# Step 4: View results
python src/main.py ~/Media --db_path media.db --report
```

---

## 🌐 Web Viewer (Optional GUI)

For more advanced features like:

- Dry-run previews before deleting/exporting
- Multi-file selection with checkboxes
- Filter + sort + export buttons
- Web-based interface to view and manage duplicates

➡️ See the [Web Viewer Interface](viewer/README.md) for more information.


## Added --dry-run option

python src/main.py ~/Downloads --db_path test.db --dry-run --debug

pytest tests/test_integration.py -v -k test_dry_run_scan

pytest tests/test_integration.py -v -k test_real_scan_creates_db

pytest tests/integration -v

pytest tests/unit -v

uvicorn viewer.main:app --reload
