from PySide6.QtWidgets import QLabel, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTabWidget
from services import books

class MainWindow(QMainWindow):
    def __init__(self, librarian):
        super().__init__() # allow access to methods & properties of QMainWindow

        self._librarian = librarian
        self.setup_ui()
        self.load_books()

    def setup_ui(self):     
        self.setWindowTitle("Library Management System")
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        greeting_message = QLabel(f"Welcome, {self._librarian.get_first_name()}")

        self._log_out_button = QPushButton("Log out")
        top_bar.addWidget(greeting_message)
        top_bar.addStretch()
        top_bar.addWidget(self._log_out_button)
        layout.addLayout(top_bar)

        # search + edit 
        controls = QHBoxLayout()
        self._search_bar = QLineEdit()
        self._search_button = QPushButton("Search")
        self._add_book_button = QPushButton("Add Book")
        self._edit_book_button = QPushButton("Edit Book")
        controls.addWidget(QLabel("Search"))
        controls.addWidget(self._search_bar)
        controls.addWidget(self._search_button)
        controls.addStretch()
        controls.addWidget(self._add_book_button)
        controls.addWidget(self._edit_book_button)

        # books table
        self._book_table = QTableWidget()
        self._book_table.setColumnCount(6)
        self._book_table.setHorizontalHeaderLabels(["Book ID", "Title", "Author", "Genre", "ISBN", "Year"])
        self._book_table.setEditTriggers(QTableWidget.NoEditTriggers) # read only
        self._book_table.setSelectionBehavior(QTableWidget.SelectRows) # select whole rows
        self._book_table.setSelectionMode(QTableWidget.SingleSelection) #one row at a time

        # books tab holds the controls and the table
        books_tab = QWidget()
        books_layout = QVBoxLayout()
        books_layout.addLayout(controls)
        books_layout.addWidget(self._book_table)
        books_tab.setLayout(books_layout)

        # one tab for each feature area
        tabs = QTabWidget()
        tabs.addTab(books_tab, "Books")
        tabs.addTab(QWidget(), "Loans")
        tabs.addTab(QWidget(), "Overdue")
        tabs.addTab(QWidget(), "Fines")
        tabs.addTab(QWidget(), "Audit Log")
        layout.addWidget(tabs)

        # shows errors from the buttons above
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        central_widget.setLayout(layout)
        
    def load_books(self):
        # the whole table is refilled every time
        books_rows = books.get_all_books()
        self._book_table.setRowCount(len(books_rows))

        for row_index, book in enumerate(books_rows):
            author = author = f'{book["first_name"]} {book["last_name"]}'

            year = ""
            if book["publication_year"] is not None:
                year = str(book["publication_year"])

            self._book_table.setItem(row_index, 0, QTableWidgetItem(str(book["book_id"])))
            self._book_table.setItem(row_index, 1, QTableWidgetItem(book["title"]))
            self._book_table.setItem(row_index, 2, QTableWidgetItem(author))
            self._book_table.setItem(row_index, 3, QTableWidgetItem(book["genre_name"] or ""))
            self._book_table.setItem(row_index, 4, QTableWidgetItem(book["isbn"]))
            self._book_table.setItem(row_index, 5, QTableWidgetItem(year))
    
        self._book_table.resizeColumnsToContents()
    



