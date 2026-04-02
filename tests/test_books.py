"""
Unit tests for the Books API.

All DynamoDB calls are mocked so no real AWS resources are needed.
Run with:  pytest tests/unit/ -v
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app
# from src.services import create_book_service
# from tests.test_services import FakeDB

client = TestClient(app)

VALID_BOOK = {
    "id": "/books/550e8400-e29b-41d4-a716-446655440000",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Awesome book for beginners in Fancy.",
    "serial": "C040102",
    "pk": "550e8400-e29b-41d4-a716-446655440000",
}

# ---------------------------------------------------------------------------
# POST /api/books
# ---------------------------------------------------------------------------

class TestCreateBook:

    @patch("src.main.db.get_book", return_value=None)
    @patch("src.main.db.put_book")
    def test_create_book_success(self, mock_put, mock_get):
        """Should return 201 when all fields are present and db write succeeds."""
        mock_put.return_value = None
        response = client.post("/api/books", json=VALID_BOOK)
        assert response.status_code == 201
        mock_put.assert_called_once_with(VALID_BOOK)

    @pytest.mark.parametrize("missing_field", ["id", "author", "name", "note", "serial"])
    @patch("src.main.db.put_book")
    def test_create_book_missing_field(self, mock_put, missing_field):
        """Should return 400 when any required field is missing."""
        payload = {k: v for k, v in VALID_BOOK.items() if k != missing_field}
        response = client.post("/api/books", json=payload)
        assert response.status_code == 400
        # FastAPI 400 body contains details about the bad field
        body = response.json()
        assert "detail" in body

    @patch("src.main.db.put_book")
    def test_create_book_empty_field(self, mock_put, ):
        """Should return 400 when a field is present but empty."""
        payload = {**VALID_BOOK, "name": ""}
        response = client.post("/api/books", json=payload)
        assert response.status_code == 400

    @patch("src.main.db.get_book", return_value=None)
    @patch("src.main.db.put_book", side_effect=Exception("DynamoDB unavailable"))
    def test_create_book_db_error(self, mock_put, mock_get):
        """Should return 500 when the database raises an unexpected exception."""
        response = client.post("/api/books", json=VALID_BOOK)
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    @patch("src.main.db.put_book")
    def test_create_book_returns_json(self, mock_put):
        """Response body should be valid JSON with a success message."""
        mock_put.return_value = None
        response = client.post("/api/books", json=VALID_BOOK)
        assert response.headers["content-type"].startswith("application/json")

    @patch("src.main.db.put_book")
    def test_create_book_wrong_content_type(self, mock_put):
        """Sending plain text instead of JSON should return 400."""
        response = client.post(
            "/api/books",
            content="not json",
            headers={"content-type": "text/plain"},
        )
        assert response.status_code == 400

    @patch("src.main.db.get_book", return_value=VALID_BOOK)
    @patch("src.main.db.put_book")
    def test_create_book_duplicate(self, mock_put, mock_get):
        """Should return 409 if book with same ID already exists."""
        response = client.post("/api/books", json=VALID_BOOK)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

        mock_put.assert_not_called()

    @patch("src.main.db.get_book", return_value=None)
    @patch("src.main.db.put_book")
    def test_create_book_invalid_id_format(self, mock_put, mock_get):
        bad_payload = {**VALID_BOOK, "id": "wrong-format"}  # not using prefix '/books/'

        response = client.post("/api/books", json=bad_payload)

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

        mock_put.assert_not_called()


# ---------------------------------------------------------------------------
# GET /api/books/{id}
# ---------------------------------------------------------------------------

class TestGetBook:

    @patch("src.main.db.get_book", return_value=VALID_BOOK)
    def test_get_book_success(self, mock_get):
        """Should return 200 and the full book payload when the id exists."""
        response = client.get("/api/books/id1")
        assert response.status_code == 200
        assert response.json() == VALID_BOOK
        mock_get.assert_called_once_with("id1")

    @patch("src.main.db.get_book", return_value=None)
    def test_get_book_not_found(self, mock_get):
        """Should return 404 when the book does not exist."""
        response = client.get("/api/books/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("src.main.db.get_book", side_effect=Exception("Connection timeout"))
    def test_get_book_db_error(self, mock_get):
        """Should return 500 when the database raises an unexpected exception."""
        response = client.get("/api/books/id1")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    @patch("src.main.db.get_book", return_value=VALID_BOOK)
    def test_get_book_response_schema(self, mock_get):
        """Response should contain all required book fields."""
        response = client.get("/api/books/id1")
        body = response.json()
        for field in ["id", "author", "name", "note", "serial"]:
            assert field in body, f"Missing field: {field}"

    @patch("src.main.db.get_book", return_value=VALID_BOOK)
    def test_get_book_content_type(self, mock_get):
        """Response content-type should be application/json."""
        response = client.get("/api/books/id1")
        assert response.headers["content-type"].startswith("application/json")


# ---------------------------------------------------------------------------
# GET /api/books
# ---------------------------------------------------------------------------

class TestListBooks:

    @patch("src.main.db.list_books", return_value=[
        {
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Awesome book",
            "serial": "C040102",
            "pk": "id1",
        },
        {
            "id": "/books/id2",
            "author": "/authors/id2",
            "name": "Advanced Fancy",
            "note": "Advanced stuff",
            "serial": "C040103",
            "pk": "id2",
        },
    ])
    def test_list_books_success(self, mock_list):
        """Should return 200 and a list of books without internal fields."""
        response = client.get("/api/books")

        assert response.status_code == 200
        body = response.json()

        assert isinstance(body, list)
        assert len(body) == 2

        # ensure pk is NOT exposed
        for item in body:
            assert "pk" not in item

    @patch("src.main.db.list_books", return_value=[])
    def test_list_books_empty(self, mock_list):
        """Should return empty list when no books exist."""
        response = client.get("/api/books")

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.main.db.list_books", return_value=[
        {
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Awesome book",
            "serial": "C040102",
            "pk": "id1",
        }
    ])
    def test_list_books_schema(self, mock_list):
        """Each item should contain required public fields only."""
        response = client.get("/api/books")
        body = response.json()

        required_fields = ["id", "author", "name", "note", "serial"]

        for item in body:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"

    @patch("src.main.db.list_books", return_value=[
        {
            "id": "/books/id1",
            "author": "/authors/id1",
            "name": "Fancy Tech",
            "note": "Awesome book",
            "serial": "C040102",
            "pk": "id1",
        }
    ])
    def test_list_books_content_type(self, mock_list):
        """Response content-type should be application/json."""
        response = client.get("/api/books")
        assert response.headers["content-type"].startswith("application/json")
