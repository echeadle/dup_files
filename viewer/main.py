import io
import csv
from pathlib import Path
import sqlite3
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
DB_PATH = BASE_DIR.parent / "test_hashes.db"  # 👈 adjust if needed

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

def get_duplicate_groups(db_path):
    """Return a dict of {hash: [path1, path2, ...]} for hashes with duplicates."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hash FROM file_paths
        GROUP BY hash
        HAVING COUNT(path) > 1
    """)
    hashes = [row[0] for row in cursor.fetchall()]

    duplicates = {}
    for h in hashes:
        cursor.execute("SELECT path FROM file_paths WHERE hash = ?", (h,))
        paths = [row[0] for row in cursor.fetchall()]
        duplicates[h] = paths

    conn.close()
    return duplicates

@app.get("/")
def index(request: Request):
    duplicates = get_duplicate_groups(DB_PATH)
    return templates.TemplateResponse("index.html", {"request": request, "duplicates": duplicates})

@app.get("/export/csv")
def export_csv():
    duplicates = get_duplicate_groups(DB_PATH)

    # Write CSV to in-memory file
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hash", "path"])

    for hash_val, paths in duplicates.items():
        for path in paths:
            writer.writerow([hash_val, path])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=duplicates.csv"
    })
    
@app.get("/export/markdown")
def export_markdown():
    duplicates = get_duplicate_groups(DB_PATH)

    output = io.StringIO()

    for hash_val, paths in duplicates.items():
        output.write(f"### Hash: `{hash_val}`\n")
        for path in paths:
            output.write(f"- `{path}`\n")
        output.write("\n")

    output.seek(0)
    return StreamingResponse(output, media_type="text/markdown", headers={
        "Content-Disposition": "attachment; filename=duplicates.md"
    })
    
from fastapi.responses import JSONResponse

@app.get("/export/json")
def export_json():
    duplicates = get_duplicate_groups(DB_PATH)
    return JSONResponse(content=duplicates, headers={
        "Content-Disposition": "attachment; filename=duplicates.json"
    })


