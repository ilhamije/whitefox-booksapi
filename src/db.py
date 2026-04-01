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



def create_book(book: dict):
    mock_table.append(book)


def get_book(raw_id: str):
    for item in mock_table:
        if item["pk"] == raw_id:
            return {k: v for k, v in item.items() if k != "pk"}
        return None


def list_books():
    return mock_table
