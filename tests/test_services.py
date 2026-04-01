import pytest
from src.services import (
    create_book_service,
    get_book_service,
    list_books_service,
)


# ---------------------------------------------------------------------------
# Fake DB implementation for testing
# ---------------------------------------------------------------------------

class FakeDB:
    def __init__(self):
        self.storage = {}
        self.put_called = False

    def put_book(self, book: dict):
        self.put_called = True
        book_id = book["id"].split("/")[-1]
        self.storage[book_id] = book

    def get_book(self, book_id: str):
        return self.storage.get(book_id)

    def list_books(self):
        return list(self.storage.values())


VALID_BOOK = {
    "id": "/books/id1",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Nice",
    "serial": "C1",
}


# ---------------------------------------------------------------------------
# create_book_service
# ---------------------------------------------------------------------------

def test_create_book_calls_db():
    db = FakeDB()

    create_book_service(VALID_BOOK, db)

    assert db.put_called is True
    assert "id1" in db.storage


def test_create_book_duplicate():
    db = FakeDB()
    db.put_book(VALID_BOOK)

    with pytest.raises(ValueError) as exc:
        create_book_service(VALID_BOOK, db)

    assert "already exists" in str(exc.value)


# ---------------------------------------------------------------------------
# get_book_service
# ---------------------------------------------------------------------------

def test_get_book_success():
    db = FakeDB()
    db.put_book(VALID_BOOK)

    result = get_book_service("id1", db)

    assert result == VALID_BOOK


def test_get_book_not_found():
    db = FakeDB()

    result = get_book_service("id1", db)

    assert result is None


# ---------------------------------------------------------------------------
# list_books_service
# ---------------------------------------------------------------------------

def test_list_books():
    db = FakeDB()
    db.put_book(VALID_BOOK)

    result = list_books_service(db)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "/books/id1"


def test_list_books_empty():
    db = FakeDB()

    result = list_books_service(db)

    assert result == []
