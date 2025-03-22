from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import os

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

# Templating and static files
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def home(request: Request):
    global CURRENT_DB_PATH
    db_file = CURRENT_DB_PATH
    data = load_duplicates(db_file)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "duplicates": data,
        "db_filename": db_file.name
    })


@app.post("/upload")
async def upload_db(db_file: UploadFile = File(...)):
    global CURRENT_DB_PATH

    # Ensure upload directory exists
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    with open(UPLOAD_DB_PATH, "wb") as out_file:
        shutil.copyfileobj(db_file.file, out_file)

    # Update active DB path
    CURRENT_DB_PATH = UPLOAD_DB_PATH

    return RedirectResponse(url="/", status_code=303)
