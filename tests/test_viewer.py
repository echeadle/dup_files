from fastapi.testclient import TestClient
from viewer.main import app
from bs4 import BeautifulSoup

client = TestClient(app)

def test_homepage_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Duplicate File Viewer" in response.text

def test_sidebar_hashes_displayed():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    sidebar_items = soup.select("li.sidebar-item")
    assert len(sidebar_items) > 0  # At least one group
    for item in sidebar_items:
        assert item["data-hash"]  # Should have hash attribute

def test_csv_export():
    response = client.get("/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "hash,path" in response.text  # header row

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
    assert "### Hash:" in response.text

def test_search_input_present():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    search = soup.select_one("input#searchInput")
    assert search is not None

def test_clear_filter_button_present():
    response = client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")
    button = soup.select_one("button#clearFilterBtn")
    assert button is not None
    assert "Clear" in button.text
