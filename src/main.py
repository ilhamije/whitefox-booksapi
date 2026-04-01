import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.services import (
    create_book_service,
    get_book_service,
    list_books_service,
)

ENV = os.getenv("ENV", "local")

if ENV == "test":
    from src import db as db_module
else:
    from src import db_dynamo as db_module


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

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
        return db_module.create_book(book)

    @staticmethod
    def get_book(book_id: str):
        return db_module.get_book(book_id)

    @staticmethod
    def list_books():
        return db_module.list_books()


# --- ROUTES ---
@app.post("/api/books", status_code=201)
def create_book_api(book: Book):
    logger.info(f"POST /api/books - payload id={book.id}")

    try:
        create_book_service(book.model_dump(), db)
        logger.info(f"Book created successfully: id={book.id}")
        return {"message": "Book created"}

    except ValueError as e:
        msg = str(e)
        logger.warning(f"Create book failed: {msg}")

        if "already exists" in msg:
            raise HTTPException(status_code=409, detail=msg)
        else:
            raise HTTPException(status_code=400, detail=msg)

    except Exception as e:
        logger.error(
            f"Unexpected error in create_book_api: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/books/{book_id}")
def get_book_api(book_id: str):
    logger.info(f"GET /api/books/{book_id}")

    try:
        book = get_book_service(book_id, db)
        if not book:
            logger.warning(f"Book not found: id={book_id}")
            raise HTTPException(status_code=404, detail="Book not found")

        logger.info(f"Book retrieved: id={book_id}")
        return book

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in get_book_api: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/books")
def list_books_api():
    logger.info("GET /api/books")

    try:
        books = list_books_service(db)
        logger.info(f"Books retrieved: count={len(books)}")

        return [
            {k: v for k, v in item.items() if k != "pk"}
            for item in books
        ]

    except Exception as e:
        logger.error(
            f"Unexpected error in list_books_api: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
