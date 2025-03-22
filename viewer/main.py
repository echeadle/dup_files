import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from viewer.utils import load_duplicates

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "viewer" / "templates"
STATIC_DIR = BASE_DIR / "viewer" / "static"
DEFAULT_DB_PATH = BASE_DIR / "test_hashes.db"
UPLOAD_DIR = BASE_DIR / "uploaded"
EXPORT_DIR = BASE_DIR / "exported"

UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CURRENT_DB_PATH = DEFAULT_DB_PATH
LAST_UPLOAD_FILENAME = None


@app.get("/", response_class=HTMLResponse)
def home(request: Request, msg: str = None):
    db_file = CURRENT_DB_PATH
    data = load_duplicates(db_file)

    total_hashes = len(data)
    total_files = sum(len(paths) for paths in data.values())
    avg_files_per_hash = round(total_files / total_hashes, 2) if total_hashes else 0

    # Detect paths that appear in multiple hashes (for highlighting)
    from collections import Counter
    all_paths = [path for paths in data.values() for path in paths]
    path_counts = Counter(all_paths)
    duplicate_paths = set(p for p, c in path_counts.items() if c > 1)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "duplicates": data,
        "db_filename": LAST_UPLOAD_FILENAME or db_file.name,
        "toast_msg": msg,
        "is_uploaded": bool(LAST_UPLOAD_FILENAME),
        "duplicate_paths": duplicate_paths,
        "summary": {
            "hashes": total_hashes,
            "files": total_files,
            "avg": avg_files_per_hash
        }
    })


@app.post("/upload")
async def upload_db(db_file: UploadFile = File(...)):
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
    confirm: Optional[str] = Form(None)
):
    if not paths or len(paths) == 0:
        # No files selected
        return RedirectResponse(url="/?msg=empty", status_code=303)

    if preview == "true" and confirm != "true":
        # Dry-run preview mode
        return templates.TemplateResponse("preview.html", {
            "request": request,
            "action": action,
            "paths": paths
        })

    # Confirmed: proceed with delete/export
    successful = []
    failed = []

    for path in paths:
        try:
            if action == "delete":
                os.remove(path)
            elif action == "export":
                EXPORT_DIR.mkdir(exist_ok=True)
                shutil.copy(path, EXPORT_DIR / Path(path).name)
            successful.append(path)
        except Exception as e:
            failed.append((path, str(e)))

    # Log file paths
    logfile = EXPORT_DIR / f"{action}ed.log"
    with open(logfile, "a") as log:
        for path in successful:
            log.write(f"{datetime.now().isoformat()} | {path}\n")

    return RedirectResponse(url=f"/?msg={action}", status_code=303)

