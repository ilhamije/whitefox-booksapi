import os

mock_table = [
    {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Fancy Tech",
        "note": "Awesome book for beginners in Fancy.",
        "serial": "C040102",
        "pk": "id1",
    },
    {
        "id": "/books/id2",
        "author": "/authors/id2",
        "name": "Advanced Fancy",
        "note": "Great book for advanced users of Fancy.",
        "serial": "C040103",
        "pk": "id2",
    },
    {
        "id": "/books/id3",
        "author": "/authors/id1",
        "name": "Fancy for Dummies",
        "note": "A book for dummies about Fancy.",
        "serial": "C040104",
        "pk": "id3",
    },
]

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "books")
REGION = os.environ.get("APP_REGION", "us-east-1")
# you should see books-api-dev-books
print(f"[DEBUG] Using table: {TABLE_NAME}")

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

    return {k: v for k, v in item.items() if k != "pk"}


def list_books():
    return mock_table
