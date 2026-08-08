class Book:

    def __init__(self, book_id, isbn, title, publication_year, publisher, genre_id):
        self._book_id = book_id
        self._isbn = isbn
        self._title = title
        self._publication_year = publication_year
        self._publisher = publisher
        self._genre_id = genre_id

    @classmethod
    def from_row(cls, row):
        return cls(row["book_id"],
                   row["isbn"],
                   row["title"],
                   row["publication_year"],
                   row["publisher"],
                   row["genre_id"])

    def __str__(self): # not used in UI. used for debugging and logging consistency
        return f"{self._title} ({self._isbn})"
    
    def get_book_id(self):
        return self._book_id

    def get_isbn(self):
        return self._isbn

    def get_title(self):
        return self._title

    def get_publication_year(self):
        return self._publication_year

    def get_publisher(self):
        return self._publisher

    def get_genre_id(self):
        return self._genre_id

