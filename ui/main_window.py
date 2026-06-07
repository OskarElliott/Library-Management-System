from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem

class MainWindow(QMainWindow):
    def __init__(self, user, conn):
        super().__init__()
        self.user = user
        self.conn = conn

        self.setWindowTitle(f"Library ({user.username}), {user.role_name}")
        self.resize(700, 400)

        self.table = QTableWidget()
        self.setCentralWidget(self.table)

        self._load_books()

    def _load_books(self):
        rows = self.conn.execute(
            """
            SELECT b.title,
                   GROUP_CONCAT(a.last_name, ', ') AS authors,
                   g.name AS genre,
                   b.publication_year AS year,
                   (SELECT COUNT(*) FROM BookCopies c
                    WHERE c.book_id = b.book_id AND c.status = 'available') AS available
            FROM Books b
            LEFT JOIN Genres g ON g.genre_id = b.genre_id
            LEFT JOIN BookAuthors ba ON ba.book_id = b.book_id
            LEFT JOIN Authors a ON a.author_id = ba.author_id
            GROUP BY b.book_id
            ORDER BY b.title
            """
        ).fetchall()

        headers = ["Title", "Authors", "Genre", "Year", "Available"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [row["title"], row["authors"], row["genre"], row["year"], row["available"]]
            for col_index, value in enumerate(values):
                text = "" if value is None else str(value)
                self.table.setItem(row_index, col_index, QTableWidgetItem(text))

            self.table.resizeColumnsToContents()
     