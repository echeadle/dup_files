from fastapi.testclient import TestClient
from viewer.main import app
from bs4 import BeautifulSoup

client = TestClient(app)

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
