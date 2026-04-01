from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.services import (
    create_book_service,
    get_book_service,
    list_books_service,
)
from src import db as db_module

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
        db_module.create_book(book)

    @staticmethod
    def get_book(book_id: str):
        return db_module.get_book(book_id)

    @staticmethod
    def list_books():
        return db_module.list_books()


# --- ROUTES ---
@app.post("/api/books", status_code=201)
def create_book_api(book: Book):
    try:
        create_book_service(book.model_dump(), db)
        return {"message": "Book created"}

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/books/{book_id}")
def get_book_api(book_id: str):
    try:
        book = get_book_service(book_id, db)
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
        books = list_books_service(db)

        return [
            {k: v for k, v in item.items() if k != "pk"}
            for item in books
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
