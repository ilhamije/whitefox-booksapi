def create_book_service(book: dict, db):
    """
    Create new book data
    """
    db.put_book(book)


def get_book_service(book_id: str, db):
    """
    Retrieving a book.
    """
    book = db.get_book(book_id)
    return book


def list_books_service(db):
    """
    Listing books.
    """
    books = db.list_books()
    return books
