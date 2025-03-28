import re
from fastapi.testclient import TestClient
from fastapi import HTTPException
from viewer.main import app
from bs4 import BeautifulSoup
from pathlib import Path
import sqlite3

client = TestClient(app)

def _get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Establishes a connection to the database."""
    return sqlite3.connect(db_path)

def test_homepage_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Duplicate File Viewer" in response.text or "Navigation" in response.text

def test_sidebar_hashes_displayed():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    nav_links = soup.select(".sidebar ul li a")
    assert len(nav_links) >= 2  # Ensure some navigation items exist
    expected_links = ["/", "/preview", "/config/filetypes"]
    hrefs = [a.get("href") for a in nav_links]
    for link in expected_links:
        assert link in hrefs

def test_csv_export():
    response = client.get("/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "hash,paths" in response.text  # Match lowercase header

def test_json_export():
    response = client.get("/export/json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, dict)

def test_markdown_export():
    response = client.get("/export/markdown")
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "# Duplicate Summary" in response.text

def test_search_input_present():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    search = soup.select_one("input[type='text']") or soup.select_one("input.search-input")
    assert search is not None

def test_clear_filter_button_present():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    button = soup.find("button", string=lambda t: t and "Clear" in t)
    assert button is not None
    
def test_sidebar_contains_report_links():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("ul.sidebar-links a")

    expected_routes = ["/export/csv", "/export/json", "/export/markdown"]
    found_routes = [link["href"] for link in links]

    for route in expected_routes:
        assert route in found_routes, f"Missing link: {route}"

from fastapi.responses import StreamingResponse
from datetime import datetime
import io

@app.get("/export/markdown")
def export_markdown():
    """Exports duplicate data to a Markdown file."""
    try:
        with _get_db_connection() as conn:
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
    
def test_excluded_dirs_editor_renders():
    response = client.get("/config/excludes")
    assert response.status_code == 200
    assert "Excluded Directory Editor" in response.text

def test_reset_redirects_to_home():
    response = client.get("/reset")
    assert response.status_code == 200

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    toast = soup.select_one("div.toast")
    assert toast is not None
    assert "Screen reset. No data displayed." in toast.text

