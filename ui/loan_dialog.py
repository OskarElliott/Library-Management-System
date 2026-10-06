from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout
from services import books, users
from ui.formatting import REQUIRED_MARK, to_text

class IssueLoanDialog(QDialog):
    def __init__(self, librarian):
        super().__init__()

        self._librarian = librarian
        self._all_books = books.get_all_books()

        self._setup_ui()
        self._load_borrowers()
        self._filter_books("")

    def _setup_ui(self):
        self.setWindowTitle("Issue Loan")
        self.resize(700, 560)

        layout = QVBoxLayout()
        form = QFormLayout()

        self._borrower_box = QComboBox()
        self._eligibility_label = QLabel("")
        self._filter_field = QLineEdit()
        self._title_list = QListWidget()
        self._copy_box = QComboBox()

        form.addRow("Borrower" + REQUIRED_MARK, self._borrower_box)
        form.addRow(self._eligibility_label)
        form.addRow("Search", self._filter_field)
        form.addRow("Title" + REQUIRED_MARK, self._title_list)
        form.addRow("Copy" + REQUIRED_MARK, self._copy_box)

        layout.addLayout(form)

        self._error_label = QLabel("")
        layout.addWidget(self._error_label)

        buttons = QHBoxLayout()
        buttons.addStretch()

        self._cancel_button = QPushButton("Cancel")
        self._issue_button = QPushButton("Issue Loan")

        buttons.addWidget(self._cancel_button)
        buttons.addWidget(self._issue_button)

        layout.addLayout(buttons)

        self._cancel_button.clicked.connect(self.reject)
        self._filter_field.textChanged.connect(self._filter_books)
        self._issue_button.setEnabled(False)

        self.setLayout(layout)

    def _load_borrowers(self):
        self._borrower_box.addItem("-- Select Borrower --", None)

        for borrower in users.get_borrowers():
            if borrower["role_name"] == "teacher":
                group = "teacher"

            else: 
                group = borrower["homeroom"]

            display = f'{borrower["last_name"]}, {borrower["first_name"]} ({group})'
            self._borrower_box.addItem(display, borrower["user_id"])

    def _filter_books(self, text):
        term = text.strip().lower()

        self._title_list.clear()

        for book in self._all_books:
            title = to_text(book["title"])
            author = f"{to_text(book["first_name"])} {to_text(book["last_name"])}".strip()

            if term in title.lower() or term in author.lower():
                item = QListWidgetItem(f"{title} by {author}")
                item.setData(Qt.UserRole, book["book_id"])
                self._title_list.addItem(item)
