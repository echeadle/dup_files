import sys
from pathlib import Path
import os
import sqlite3
import csv
import io
import shutil
from typing import List, Optional, Dict
from datetime import datetime
from collections import Counter

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, PlainTextResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Add BASE_DIR to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.file_scanner import load_filetypes, walk_files
from viewer.utils import load_duplicates

# --- Constants and Configuration ---
TEMPLATES_DIR = BASE_DIR / "viewer" / "templates"
STATIC_DIR = BASE_DIR / "viewer" / "static"
DEFAULT_DB_PATH = BASE_DIR / "test_hashes.db"
UPLOAD_DIR = BASE_DIR / "uploaded"
EXPORT_DIR = BASE_DIR / "exported"
FILETYPES_CONFIG_PATH = BASE_DIR / "config" / "included_filetypes.txt"
EXCLUDED_DIRS_PATH = BASE_DIR / "config" / "excluded_dirs.txt"

UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# --- App Initialization ---
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- Global State ---
CURRENT_DB_PATH = DEFAULT_DB_PATH
LAST_UPLOAD_FILENAME = None


# --- Helper Functions ---

def get_db_connection():
    """Establishes a connection to the current database."""
    return sqlite3.connect(CURRENT_DB_PATH)

def calculate_summary(data: Dict[str, List[str]]) -> Dict[str, int | float]:
    """Calculates summary statistics for duplicate data."""
    total_hashes = len(data)
    total_files = sum(len(paths) for paths in data.values())
    avg_files_per_hash = round(total_files / total_hashes, 2) if total_hashes else 0
    return {
        "hashes": total_hashes,
        "files": total_files,
        "avg": avg_files_per_hash,
    }

def get_duplicate_paths(data: Dict[str, List[str]]) -> set[str]:
    """Detects paths that appear in multiple hashes."""
    all_paths = [path for paths in data.values() for path in paths]
    path_counts = Counter(all_paths)
    return set(p for p, c in path_counts.items() if c > 1)

def log_file_action(action: str, paths: List[str]):
    """Logs the file paths that were deleted or exported."""
    logfile = EXPORT_DIR / f"{action}ed.log"
    with open(logfile, "a") as log:
        for path in paths:
            log.write(f"{datetime.now().isoformat()} | {path}\n")

def handle_file_operation(action: str, paths: List[str]) -> tuple[List[str], List[tuple[str, str]]]:
    """Performs the file operation (delete or export) on the given paths."""
    successful = []
    failed = []
    for path in paths:
        try:
            if action == "delete":
                os.remove(path)
            elif action == "export":
                shutil.copy(path, EXPORT_DIR / Path(path).name)
            successful.append(path)
        except Exception as e:
            failed.append((path, str(e)))
    return successful, failed

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request, msg: str = None):
    """Renders the home page with duplicate file information."""
    data = load_duplicates(CURRENT_DB_PATH)
    summary = calculate_summary(data)
    duplicate_paths = get_duplicate_paths(data)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "duplicates": data,
            "db_filename": LAST_UPLOAD_FILENAME or CURRENT_DB_PATH.name,
            "toast_msg": msg,
            "is_uploaded": bool(LAST_UPLOAD_FILENAME),
            "duplicate_paths": duplicate_paths,
            "summary": summary,
        },
    )


@app.post("/upload")
async def upload_db(db_file: UploadFile = File(...)):
    """Uploads a new database file."""
    global CURRENT_DB_PATH, LAST_UPLOAD_FILENAME
    file_location = UPLOAD_DIR / db_file.filename
    with open(file_location, "wb") as f:
        content = await db_file.read()
        f.write(content)

    CURRENT_DB_PATH = file_location
    LAST_UPLOAD_FILENAME = db_file.filename
    return RedirectResponse(url="/?msg=upload", status_code=303)


@app.post("/reset-db")
def reset_to_default():
    """Resets the database to the default."""
    global CURRENT_DB_PATH, LAST_UPLOAD_FILENAME
    CURRENT_DB_PATH = DEFAULT_DB_PATH
    LAST_UPLOAD_FILENAME = None
    return RedirectResponse(url="/?msg=reset", status_code=303)


@app.post("/file-action", response_class=HTMLResponse)
async def handle_file_action(
    request: Request,
    paths: Optional[List[str]] = Form(None),
    action: str = Form(...),
    preview: Optional[str] = Form(None),
    confirm: Optional[str] = Form(None),
):
    """Handles file actions (delete or export)."""
    if not paths:
        return RedirectResponse(url="/?msg=empty", status_code=303)

    if preview == "true" and confirm != "true":
        return templates.TemplateResponse(
            request, "preview.html", {"action": action, "paths": paths}
        )

    successful, failed = handle_file_operation(action, paths)
    log_file_action(action, successful)

    return RedirectResponse(url=f"/?msg={action}", status_code=303)


@app.get("/export/csv")
def export_csv():
    """Exports duplicate data to a CSV file."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM hashes")
            hashes = cursor.fetchall()

            stream = io.StringIO()
            writer = csv.writer(stream)
            writer.writerow(["hash", "paths"])

            for (hash_val,) in hashes:
                cursor.execute(
                    "SELECT path FROM file_paths WHERE hash = ?", (hash_val,)
                )
                paths = [row[0] for row in cursor.fetchall()]
                writer.writerow([hash_val, ";".join(paths)])

            stream.seek(0)
            now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"exports-{now}.csv"

            return StreamingResponse(
                stream,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/json")
def export_json():
    """Exports duplicate data to a JSON file."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM hashes")
            hashes = cursor.fetchall()

            export_data = {}
            for (hash_val,) in hashes:
                cursor.execute(
                    "SELECT path FROM file_paths WHERE hash = ?", (hash_val,)
                )
                paths = [row[0] for row in cursor.fetchall()]
                export_data[hash_val] = paths

            now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"exports-{now}.json"
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"'
            }

            return JSONResponse(content=export_data, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from fastapi.responses import StreamingResponse
from datetime import datetime
import io

from fastapi.responses import StreamingResponse
from datetime import datetime
import io

@app.get("/export/markdown")
def export_markdown():
    """Exports duplicate data to a Markdown file."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM hashes")
            hashes = cursor.fetchall()

            stream = io.StringIO()
            stream.write("# Duplicate Summary\n\n")

            for (hash_val,) in hashes:
                cursor.execute(
                    "SELECT path FROM file_paths WHERE hash = ?", (hash_val,)
                )
                paths = [row[0] for row in cursor.fetchall()]
                if len(paths) > 1:
                    stream.write(f"### Hash: `{hash_val}`\n")
                    for path in paths:
                        stream.write(f"- {path}\n")
                    stream.write("\n")

            stream.seek(0)
            now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"exports-{now}.md"

            return StreamingResponse(
                stream,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config/filetypes", response_class=HTMLResponse)
def edit_filetypes_form(request: Request):
    """Renders the file types configuration editor."""
    try:
        with open(FILETYPES_CONFIG_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    return templates.TemplateResponse(
        request,
        "config_editor.html",
        {"request": request, "file_content": content, "msg": request.query_params.get("msg")},
    )


@app.post("/config/filetypes", response_class=HTMLResponse)
def save_filetypes_config(request: Request, content: str = Form(...)):
    """Saves the file types configuration."""
    try:
        with open(FILETYPES_CONFIG_PATH, "w") as f:
            f.write(content.strip() + "\n")
        msg = "Config updated successfully!"
    except Exception as e:
        msg = f"Error saving config: {e}"

    return RedirectResponse(url=f"/config/filetypes?msg={msg}", status_code=303)


@app.get("/config/filetypes/preview")
def preview_matching_files(dir: str):
    """Previews files matching the configured file types in a directory."""
    filetypes = load_filetypes(FILETYPES_CONFIG_PATH)
    if not os.path.isdir(dir):
        raise HTTPException(status_code=400, detail="Invalid directory")

    matches = [
        path
        for path in walk_files(dir)
        if os.path.splitext(path)[1].lower() in filetypes
    ]
    return {"matches": matches}

@app.get("/preview", response_class=HTMLResponse)
def view_preview_page(request: Request):
    return templates.TemplateResponse(request, "preview.html", {
        "request": request,
        "action": "none",
        "paths": []
    })

EXCLUDED_DIRS_PATH = BASE_DIR / "config" / "excluded_dirs.txt"

@app.get("/config/excludes", response_class=HTMLResponse)
def edit_excludes_form(request: Request):
    try:
        with open(EXCLUDED_DIRS_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    return templates.TemplateResponse(
        request,
        "config_excludes.html",
        {
            "request": request,
            "file_content": content,
            "msg": request.query_params.get("msg")
        },
    )

@app.post("/config/excludes", response_class=HTMLResponse)
def save_excludes_config(request: Request, content: str = Form(...)):
    try:
        with open(EXCLUDED_DIRS_PATH, "w") as f:
            f.write(content.strip() + "\n")
        msg = "Excluded directories updated!"
    except Exception as e:
        msg = f"Error saving file: {e}"

    return RedirectResponse(url=f"/config/excludes?msg={msg}", status_code=303)


@app.get("/reset", response_class=HTMLResponse)
def reset_viewer(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "duplicates": {},
        "duplicate_paths": [],
        "summary": {"hashes": 0, "files": 0, "avg": 0},
        "toast_msg": "Screen reset. No data displayed."
    })



