from db.connection import get_connection
from models.book import Book
from datetime import date

ACTION_ADD_BOOK = "add_book"
ACTION_EDIT_BOOK = "edit_book"
ACTION_WITHDRAW_BOOK = "withdraw_book"
ACTION_ADD_COPY = "add_copy"
ACTION_DISCARD_COPY = "discard_copy"

def get_all_books():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Books.book_id, Books.title, Books.isbn, Authors.first_name, Authors.last_name, Genres.name AS genre_name, Books.publisher, Books.publication_year
                FROM Books LEFT JOIN BookAuthors ON Books.book_id = BookAuthors.book_id
                LEFT JOIN Authors ON BookAuthors.author_id = Authors.author_id 
                LEFT JOIN Genres ON Books.genre_id = Genres.genre_id WHERE Books.is_active = 1
                ORDER BY Books.title""")

    books = cur.fetchall()
    con.close()

    return books

def get_book(book_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Books.book_id, Books.isbn, Books.title, Books.publication_year, Books.publisher, Books.genre_id
                FROM Books WHERE Books.book_id = ? AND Books.is_active = 1""", (book_id,))

    row = cur.fetchone()
    con.close()

    if row is None:
        return None

    return Book.from_row(row)

def get_book_author(book_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT Authors.first_name, Authors.last_name FROM BookAuthors
                JOIN Authors ON BookAuthors.author_id = Authors.author_id WHERE BookAuthors.book_id = ?""", (book_id,))

    row = cur.fetchone()
    con.close()

    if row is None:
        return None

    return row

def get_copies(book_id):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT copy_id, purchase_date, condition, status FROM BookCopies where book_id = ? ORDER BY copy_id", (book_id,))
    copies = cur.fetchall()

    con.close()

    return copies 

def get_all_genres():
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT genre_id, name FROM Genres ORDER BY name")

    genres = cur.fetchall()
    con.close()
    return genres

def _check_and_clean_book_fields(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name):
    isbn = isbn.strip()
    title = title.strip()
    publisher = publisher.strip() or None
    author_first_name = author_first_name.strip() or None
    author_last_name = author_last_name.strip()

    if isbn == "":
        raise ValueError("ISBN is required")
    
    if title == "":
        raise ValueError("Title is required")
    
    if genre_id is None:
        raise ValueError("Genre is required")

    if author_last_name == "":
        raise ValueError("Author last name is required")

    if publication_year == "":
        publication_year = None
    elif publication_year is not None:
        try:
            publication_year = int(publication_year)
        except ValueError:
            raise ValueError("Publication year must be a number")

        if publication_year < 0 or publication_year > 2100:
            raise ValueError("Publication year is out of range")
        
    return(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name)

def _get_or_create_author(cur, first_name, last_name): 
    # is matches null values correctly
    cur.execute("SELECT author_id FROM Authors WHERE first_name IS ? AND last_name = ?", (first_name, last_name))

    row = cur.fetchone()

    if row is not None:
        return row["author_id"]

    cur.execute("INSERT INTO Authors(first_name, last_name) VALUES(?, ?)", (first_name, last_name))

    return cur.lastrowid

def add_book(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name, librarian_id):
    (isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name) = _check_and_clean_book_fields(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name)


    con = get_connection()

    try:
        with con:
            cur = con.cursor()

            # duplicate isbn check
            cur.execute("SELECT 1 FROM Books WHERE isbn = ?", (isbn,))

            if cur.fetchone() is not None:
                raise ValueError("ISBN already exists")

            # insert book
            cur.execute("""INSERT INTO Books(isbn, title, publication_year, publisher, genre_id)
                        VALUES(?, ?, ?, ?, ?)""",(isbn, title, publication_year, publisher, genre_id,))

            book_id = cur.lastrowid

            author_id = _get_or_create_author(cur, author_first_name, author_last_name)

            cur.execute("INSERT INTO BookAuthors(book_id, author_id) VALUES(?, ?)", (book_id, author_id))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES(?,?,?,?)", (librarian_id,ACTION_ADD_BOOK,"Books", book_id,))

            return book_id

    finally: 
        con.close()

def edit_book(book_id, isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name, librarian_id):
    (isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name) = _check_and_clean_book_fields(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name)

    con = get_connection()

    try:
        with con:
            cur = con.cursor()

            # exclude the current book when checking for duplicate isbns
            cur.execute("SELECT book_id FROM Books WHERE isbn = ? AND book_id != ?", (isbn, book_id))

            if cur.fetchone() is not None:
                raise ValueError("ISBN already exists")

            cur.execute("""UPDATE Books 
                        SET isbn = ?, title = ?, publication_year = ?, publisher = ?, genre_id = ? 
                        WHERE book_id = ?""", (isbn, title, publication_year, publisher, genre_id, book_id))

            if cur.rowcount == 0:
                raise ValueError("Book not found")

            author_id = _get_or_create_author(cur, author_first_name, author_last_name)

            cur.execute("DELETE FROM BookAuthors WHERE book_id = ?", (book_id,))

            cur.execute("INSERT INTO BookAuthors(book_id, author_id) VALUES (?, ?)", (book_id, author_id))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)", (librarian_id, ACTION_EDIT_BOOK, "Books", book_id))

    finally:
        con.close()

def withdraw_book(book_id, librarian_id):
    con = get_connection()

    try:
        with con:
            cur = con.cursor()

            cur.execute("UPDATE Books SET is_active = 0 WHERE book_id = ?", (book_id,))

            if cur.rowcount == 0:
                raise ValueError("Book not found")

            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE book_id = ?", (book_id,))

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?,?,?,?)", (librarian_id, ACTION_WITHDRAW_BOOK, "Books", book_id))

    finally:
        con.close()

def add_copy(book_id, librarian_id):
    purchase_date = date.today().isoformat() # default purchase date

    con = get_connection()

    try:
        with con:
            cur = con.cursor()

            cur.execute("SELECT 1 FROM Books WHERE book_id = ? AND is_active = 1", (book_id,))
            if cur.fetchone() is None:
                raise ValueError("Book not found")

            cur.execute("INSERT INTO BookCopies(book_id, purchase_date) VALUES (?,?)",(book_id, purchase_date))

            copy_id = cur.lastrowid

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES (?,?,?,?)", (librarian_id, ACTION_ADD_COPY, "BookCopies", copy_id))

            return copy_id
    finally:
        con.close()

def discard_copy(copy_id, librarian_id):
    con = get_connection()

    try:
        with con:
            cur = con.cursor()

            cur.execute("UPDATE BookCopies SET status = 'discarded' WHERE copy_id = ? AND status != 'discarded'", (copy_id,))

            if cur.rowcount == 0:
                raise ValueError("Copy not found or already discarded")

            cur.execute("INSERT INTO AuditLog(user_id, action, table_name, record_id) VALUES(?, ?, ?, ?)", (librarian_id, ACTION_DISCARD_COPY, "BookCopies", copy_id))

    finally: 
        con.close()