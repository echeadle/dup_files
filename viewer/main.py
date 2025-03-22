from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import os
from collections import Counter
from typing import List, Optional
from viewer.utils import load_duplicates  # Make sure this is your function to read the DB

app = FastAPI()

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

# Database state
DEFAULT_DB_PATH = Path("test_hashes.db")  # adjust as needed
UPLOAD_DB_PATH = UPLOADS_DIR / "uploaded.db"
CURRENT_DB_PATH = DEFAULT_DB_PATH
LAST_UPLOAD_FILENAME = None
EXPORT_DIR = Path("exported")

# Templating and static files
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def home(request: Request, msg: str = None):
    db_file = CURRENT_DB_PATH
    data = load_duplicates(db_file)

    total_hashes = len(data)
    total_files = sum(len(paths) for paths in data.values())
    avg_files_per_hash = round(total_files / total_hashes, 2) if total_hashes else 0

    # Flatten and count all paths
    all_paths = [path for paths in data.values() for path in paths]
    path_counts = Counter(all_paths)
    duplicate_paths = set(path for path, count in path_counts.items() if count > 1)

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

    # Save uploaded file
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    with open(UPLOAD_DB_PATH, "wb") as out_file:
        shutil.copyfileobj(db_file.file, out_file)

    # Track uploaded name and switch DB
    LAST_UPLOAD_FILENAME = db_file.filename
    CURRENT_DB_PATH = UPLOAD_DB_PATH

    return RedirectResponse(url="/?msg=upload", status_code=303)


@app.post("/reset-db")
def reset_db():
    global CURRENT_DB_PATH, LAST_UPLOAD_FILENAME
    CURRENT_DB_PATH = DEFAULT_DB_PATH
    LAST_UPLOAD_FILENAME = None
    return RedirectResponse(url="/?msg=reset", status_code=303)

@app.post("/delete")
async def delete_or_export(request: Request):
    form = await request.form()
    action = form.get("action")
    paths = form.getlist("paths")

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

    # You can pass a summary back or redirect with query
    return RedirectResponse(url="/?msg=" + action, status_code=303)



EXPORT_DIR = Path("exported")
EXPORT_DIR.mkdir(exist_ok=True)

@app.post("/file-action", response_class=HTMLResponse)
async def handle_file_action(request: Request,
                             paths: List[str] = Form(...),
                             action: str = Form(...),
                             preview: Optional[str] = Form(None),
                             confirm: Optional[str] = Form(None)):
    if preview == "true" and confirm != "true":
        # Show preview screen
        return templates.TemplateResponse("preview.html", {
            "request": request,
            "action": action,
            "paths": paths
        })

    # Perform actual action
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

    # TODO: You could write to a log file here if needed

    return RedirectResponse(url=f"/?msg={action}", status_code=303)



