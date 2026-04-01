from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class Book(BaseModel):
    id: str
    author: str
    name: str = Field(min_length=1)
    note: str
    serial: str


class db:
    @staticmethod
    def put_book(book: dict):
        create_book(book)

    @staticmethod
    def get_book(book_id: str):
        return get_book(book_id)


mock_table = [
    {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Fancy Tech",
        "note": "Awesome book for beginners in Fancy.",
        "serial": "C040102",
        "pk": "id1"
    },
    {
        "id": "/books/id2",
        "author": "/authors/id2",
        "name": "Advanced Fancy",
        "note": "Great book for advanced users of Fancy.",
        "serial": "C040103",
        "pk": "id2"
    },
    {
        "id": "/books/id3",
        "author": "/authors/id1",
        "name": "Fancy for Dummies",
        "note": "A book for dummies about Fancy.",
        "serial": "C040104",
        "pk": "id3"
    }
]


def get_table():
    class MockTable:
        def put_item(self, Item):
            mock_table.append(Item)

        def get_item(self, Key):
            for item in mock_table:
                if item.get("pk") == Key["pk"]:
                    return {"Item": item}
            return {}

    return MockTable()


def create_book(book: dict):
    table = get_table()
    book_id = book["id"].split("/")[-1]

    item = {**book, "pk": book_id}
    table.put_item(Item=item)


def get_book(book_id: str):
    table = get_table()
    response = table.get_item(Key={"pk": book_id})
    item = response.get("Item")

    if not item:
        return None

    item.pop("pk", None)
    return item


# --- ROUTES ---
@app.post("/api/books", status_code=201)
def create_book_api(book: Book):
    try:
        db.put_book(book.model_dump())
        return {"message": "Book created"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/books/{book_id}")
def get_book_api(book_id: str):
    try:
        book = db.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/books")
def list_books_api():
    try:
        return mock_table
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
