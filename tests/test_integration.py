import os
import pytest
import requests
import uuid

# Base URL for local development. By default uvicorn runs on http://127.0.0.1:8000
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

def test_full_book_lifecycle():
    """
    Integration test that acts as a real client.
    Requires local DynamoDB and FastAPI app to be running.
    """
    # Check if API is running
    try:
        requests.get(f"{BASE_URL}/books", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip(f"API is not reachable at {BASE_URL}. Ensure uvicorn and DynamoDB are running via 'Local Deployment' steps.")

    # Generate a random ID
    unique_id = str(uuid.uuid4())
    book_id_path = f"/books/{unique_id}"

    new_book = {
        "id": book_id_path,
        "author": "/authors/integration-test",
        "name": f"Integration Book {unique_id}",
        "note": "A book created during integration testing",
        "serial": "INT-12345"
    }

    # 1. Create the book
    post_res = requests.post(f"{BASE_URL}/books", json=new_book)
    assert post_res.status_code == 201, f"Failed to create book: {post_res.text}"

    # 2. Retrieve the book by raw ID
    get_res = requests.get(f"{BASE_URL}/books/{unique_id}")
    assert get_res.status_code == 200, "Failed to retrieve book"
    
    saved_book = get_res.json()
    assert saved_book["name"] == new_book["name"]
    assert saved_book["serial"] == new_book["serial"]
    assert saved_book["note"] == new_book["note"]

    # 3. Retrieve all books
    list_res = requests.get(f"{BASE_URL}/books")
    assert list_res.status_code == 200
    all_books = list_res.json()
    
    assert any(b["id"] == book_id_path for b in all_books), "New book not found in list"
