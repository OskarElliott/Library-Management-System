
import json
from urllib.parse import urlencode
from urllib.request import urlopen


BOOKS_URL = "https://openlibrary.org/api/books"
TIMEOUT_SECONDS = 5


def parse_book(book):
    title = book.get("title")

    publisher = None
    publishers = book.get("publishers")
    if publishers:
        publisher = publishers[0]["name"]

    first_name = None
    last_name = None
    authors = book.get("authors")

    if authors:
        name = authors[0]["name"].strip()
        if " " in name:
            first_name, last_name = name.rsplit(" ", 1)
        elif name:
            last_name = name

    year = None
    date = book.get("publish_date")
    if date:
        for i in range(len(date) - 3):
            if date[i:i + 4].isdigit():
                year = date[i:i + 4]
                break

    return {"title": title,
            "author_first_name": first_name,
            "author_last_name": last_name,
            "publisher": publisher,
            "publication_year": year}


def lookup_isbn(isbn):
    isbn = isbn.replace(" ", "").replace("-", "")

    valid_isbn10 = (len(isbn) == 10 and isbn[:9].isdigit() and (isbn[9].isdigit() or isbn[9] == "X"))
    valid_isbn13 = len(isbn) == 13 and isbn.isdigit()

    if not (valid_isbn10 or valid_isbn13):
        raise ValueError("ISBN must be 10 or 13 digits.")

    params = {"bibkeys": f"ISBN:{isbn}",
            "format": "json",
            "jscmd": "data"}
    url = f"{BOOKS_URL}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError):
        raise ValueError("Could not reach Open Library. Enter the details by hand.")

    book = data.get(f"ISBN:{isbn}")
    if book is None:
        raise ValueError("No book found for this ISBN.")

    return parse_book(book)
