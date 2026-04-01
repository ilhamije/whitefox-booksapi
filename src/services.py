import logging

logger = logging.getLogger(__name__)


def extract_book_id(book_id: str) -> str:
    return book_id.split("/")[-1]


def validate_book_id(book_id: str):
    if not book_id.startswith("/books/"):
        raise ValueError("Invalid book id format")

    raw_id = book_id[len("/books/"):]

    if not raw_id:
        raise ValueError("Invalid book id format")


def create_book_service(book: dict, db):
    book_id = book["id"]
    logger.info(f"Creating book: {book_id}")
    validate_book_id(book_id)

    raw_id = extract_book_id(book_id)

    existing = db.get_book(raw_id)
    if existing:
        logger.warning(f"Book already exists: {book_id}")
        raise ValueError("Book already exists")

    db.put_book(book)
    logger.info(f"Book stored: {book['id']}")


def get_book_service(book_id: str, db):
    """
    Retrieving a book.
    """
    return db.get_book(book_id)


def list_books_service(db):
    """
    Listing books.
    """
    books = db.list_books()
    return books
