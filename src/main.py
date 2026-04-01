from fastapi import FastAPI, HTTPException

app = FastAPI()

mock_table = [
    {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Fancy Tech",
        "note": "Awesome book for beginners in Fancy.",
        "serial": "C040102"
    },
    {
        "id": "/books/id2",
        "author": "/authors/id2",
        "name": "Advanced Fancy",
        "note": "Great book for advanced users of Fancy.",
        "serial": "C040103"
    },
    {
        "id": "/books/id3",
        "author": "/authors/id1",
        "name": "Fancy for Dummies",
        "note": "A book for dummies about Fancy.",
        "serial": "C040104"
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

@app.get("/books/{book_id}")
def read_book(book_id: str):
    book = get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books/")
def add_book(book: dict):
    create_book(book)
    return {"message": "Book created"}


@app.get("/books/")
def list_books():
    return mock_table