from fastapi.testclient import TestClient
from bible_api.app.main import app

client = TestClient(app)

def test_read_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) > 0
    # Verify structure (BookReference has id and name, but no verses)
    first_book = response.json()[0]
    assert "id" in first_book
    assert "name" in first_book
    assert "verses" not in first_book

def test_read_chapter():
    # Genesis 1
    response = client.get("/books/1/chapters/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Text should now have normalized capitalization (only first letter uppercase)
    assert data[0]["text"].startswith("En el principio")

def test_read_chapter_cached():
    # Request again to hit cache
    response = client.get("/books/1/chapters/1")
    assert response.status_code == 200
    assert response.json()[0]["text"].startswith("En el principio")

def test_search():
    response = client.get("/search?q=principio&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "principio" in data[0]["text"].lower()

def test_random_verse():
    response = client.get("/random")
    assert response.status_code == 200
    assert "text" in response.json()
