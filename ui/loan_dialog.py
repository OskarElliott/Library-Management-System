from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout
from services import books, users, loans
from ui.formatting import REQUIRED_MARK, to_text

class IssueLoanDialog(QDialog):
    def __init__(self, librarian):
        super().__init__()

        self._librarian = librarian
        self._all_books = books.get_all_books()

        self._borrower_ok = False # set before setup so signals can read it
        self._message = ""

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
        self._error_label.setStyleSheet("color: red")
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
        self._borrower_box.currentIndexChanged.connect(self._check_borrower)
        self._title_list.itemSelectionChanged.connect(self._load_copies)
        self._copy_box.currentIndexChanged.connect(self._update_issue_button)
        self._issue_button.clicked.connect(self._issue)
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

        self._title_list.clear() # reset ui list to prevent old results from showing

        for book in self._all_books:
            title = to_text(book["title"])
            author = f'{to_text(book["first_name"])} {to_text(book["last_name"])}'.strip()

            if term in title.lower() or term in author.lower(): # match if the search term is in the title or author name
                item = QListWidgetItem(f"{title} by {author}")
                item.setData(Qt.UserRole, book["book_id"]) # stores the database id of the book in the item for later retrieval
                self._title_list.addItem(item)

        self._load_copies() # refresh dependent ui elements based on the new list of books 

    def _check_borrower(self):
        user_id = self._borrower_box.currentData()

        if user_id is None:
            self._eligibility_label.setText("")
            self._borrower_ok = False

        else:
            reasons = loans.check_eligibility(user_id)

            if reasons:
                self._eligibility_label.setText("\n".join(reasons))
                self._eligibility_label.setStyleSheet("color: red")
                self._borrower_ok = False

            else:
                self._eligibility_label.setText("Eligible to borrow")
                self._eligibility_label.setStyleSheet("")
                self._borrower_ok = True

        self._update_issue_button()

    def _load_copies(self):
        self._copy_box.clear()
        self._error_label.setText("")

        selected_items = self._title_list.selectedItems()

        if selected_items:
            book_id = selected_items[0].data(Qt.UserRole)
            copies = books.get_available_copies(book_id)

            if not copies:
                self._error_label.setText("No copies of this title are available.")

            else:
                self._copy_box.addItem("-- Select Copy --", None)

                for copy in copies:
                    self._copy_box.addItem(f'Copy {copy["copy_id"]} ({copy["condition"]})', copy["copy_id"])

        self._update_issue_button()

    def _update_issue_button(self):
        copy_chosen = self._copy_box.currentData() is not None
        self._issue_button.setEnabled(self._borrower_ok and copy_chosen)

    def _issue(self):
        self._error_label.setText("")

        user_id = self._borrower_box.currentData()
        copy_id = self._copy_box.currentData()
        today = date.today().isoformat()

        try:
            loan_id, due_date = loans.issue_loan(copy_id, user_id, self._librarian.get_user_id(), today)

        except ValueError as error:
            self._error_label.setText(str(error))
            return

        self._message = f"Loan {loan_id} issued to {self._borrower_box.currentText()}, due {due_date}."

        self.accept()

    def get_message(self):
        return self._message

    