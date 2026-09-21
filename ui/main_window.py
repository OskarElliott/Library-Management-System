from datetime import date
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from services import books, loans
from ui.book_dialog import BookDialog
from ui.formatting import to_text

class MainWindow(QMainWindow):
    def __init__(self, librarian):
        super().__init__() # allow access to methods & properties of QMainWindow

        self._librarian = librarian
        self.logged_out = False
        self._setup_ui()
        self._load_books()
        self._load_loans()
        self._load_overdue()



    def _setup_ui(self):     
        self.setWindowTitle("Library Management System")
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        greeting_message = QLabel(f"Welcome, {self._librarian.get_first_name()}")

        self._log_out_button = QPushButton("Log out")
        self._log_out_button.clicked.connect(self._log_out)
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
        self._add_book_button.clicked.connect(self._add_book)
        self._edit_book_button.clicked.connect(self._edit_book)
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
        self._loan_table = QTableWidget()
        self._loan_table.setColumnCount(6)
        self._loan_table.setHorizontalHeaderLabels(
            ["Borrower", "Title", "Copy ID", "Loan Date", "Due Date", "Days Remaining"]
        )
        self._loan_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._loan_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._loan_table.setSelectionMode(QTableWidget.SingleSelection)

        loans_tab = QWidget()
        loans_layout = QVBoxLayout()
        loans_layout.addWidget(self._loan_table)
        loans_tab.setLayout(loans_layout)
        tabs.addTab(loans_tab, "Loans")

        self._overdue_table = QTableWidget()
        self._overdue_table.setColumnCount(6)
        self._overdue_table.setHorizontalHeaderLabels(["Borrower", "Title", "Copy ID", "Loan Date", "Due Date", "Days Overdue"] )
        self._overdue_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._overdue_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._overdue_table.setSelectionMode(QTableWidget.SingleSelection)

        overdue_tab = QWidget()
        overdue_layout = QVBoxLayout()
        overdue_layout.addWidget(self._overdue_table)
        overdue_tab.setLayout(overdue_layout)
        tabs.addTab(overdue_tab, "Overdue")

        for tab_name in ["Fines", "Audit Log"]:
            tabs.addTab(QLabel("Coming soon"), tab_name)

        layout.addWidget(tabs)

        # shows errors from the buttons above
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        central_widget.setLayout(layout)

    def _log_out(self):
        self.logged_out = True
        self.close()
        
    def _load_books(self):
        # the whole table is refilled every time
        books_rows = books.get_all_books()
        self._book_table.setRowCount(len(books_rows))

        for row_index, book in enumerate(books_rows):
            author = f'{to_text(book["first_name"])} {to_text(book["last_name"])}'.strip()
 
            self._book_table.setItem(row_index, 0, QTableWidgetItem(to_text(book["book_id"])))
            self._book_table.setItem(row_index, 1, QTableWidgetItem(to_text(book["title"])))
            self._book_table.setItem(row_index, 2, QTableWidgetItem(author))
            self._book_table.setItem(row_index, 3, QTableWidgetItem(to_text(book["genre_name"])))
            self._book_table.setItem(row_index, 4, QTableWidgetItem(to_text(book["isbn"])))
            self._book_table.setItem(row_index, 5, QTableWidgetItem(to_text(book["publication_year"])))
 
        self._book_table.resizeColumnsToContents()

    def _load_loans(self):
        today = date.today().isoformat()
        loan_rows = loans.get_active_loans(today)

        self._loan_table.setRowCount(len(loan_rows))

        for row_index, loan in enumerate(loan_rows):
            borrower = f'{to_text(loan["first_name"])} {to_text(loan["last_name"])}'.strip()

            self._loan_table.setItem(row_index, 0, QTableWidgetItem(borrower))
            self._loan_table.setItem(row_index, 1, QTableWidgetItem(to_text(loan["title"])))
            self._loan_table.setItem(row_index, 2, QTableWidgetItem(to_text(loan["copy_id"])))
            self._loan_table.setItem(row_index, 3, QTableWidgetItem(to_text(loan["checkout_date"])))
            self._loan_table.setItem(row_index, 4, QTableWidgetItem(to_text(loan["due_date"])))
            self._loan_table.setItem(row_index, 5, QTableWidgetItem(to_text(int(loan["days_remaining"]))))

        self._loan_table.resizeColumnsToContents()

    def _load_overdue(self):
        today = date.today().isoformat()
        overdue_rows = loans.get_overdue_loans(today)

        self._overdue_table.setRowCount(len(overdue_rows))

        for row_index, loan in enumerate(overdue_rows):
            borrower = f'{to_text(loan["first_name"])} {to_text(loan["last_name"])}'.strip()

            self._overdue_table.setItem(row_index, 0, QTableWidgetItem(borrower))
            self._overdue_table.setItem(row_index, 1, QTableWidgetItem(to_text(loan["title"])))
            self._overdue_table.setItem(row_index, 2, QTableWidgetItem(to_text(loan["copy_id"])))
            self._overdue_table.setItem(row_index, 3, QTableWidgetItem(to_text(loan["checkout_date"])))
            self._overdue_table.setItem(row_index, 4, QTableWidgetItem(to_text(loan["due_date"])))
            self._overdue_table.setItem(row_index, 5, QTableWidgetItem(to_text(int(loan["days_overdue"]))))

        self._overdue_table.resizeColumnsToContents()

    def _add_book(self):
        dialog = BookDialog(self._librarian)

        # exec() blocks until the dialog closes and returns true only if it was accepted
        if dialog.exec():
            self._load_books()
            
    def _edit_book(self):
        row_index = self._book_table.currentRow()

        #currentRow() is -1 when nothing is selected
        if row_index == -1:
            self._status_label.setText("Select a book to edit.")
            return

        self._status_label.setText("")
        book_id = int(self._book_table.item(row_index, 0).text())
        dialog = BookDialog(self._librarian, books.get_book(book_id))

        if dialog.exec():
            self._load_books()