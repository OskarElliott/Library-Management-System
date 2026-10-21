from datetime import date
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from services import books, loans, fines, audit
from ui.book_dialog import BookDialog
from ui.loan_dialog import IssueLoanDialog
from ui.formatting import get_selected_row, set_up_table, to_text

class MainWindow(QMainWindow):
    def __init__(self, librarian):
        super().__init__() 

        self._librarian = librarian
        self.logged_out = False
        self._setup_ui()
        self._load_books()
        self._load_tables()

    def _setup_ui(self):
        self.setWindowTitle("Library Management System")
        self.resize(1280, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        greeting_message = QLabel(f"Welcome, {self._librarian.get_first_name()}")

        self._log_out_button = QPushButton("Log Out")
        self._log_out_button.clicked.connect(self._log_out)
        top_bar.addWidget(greeting_message)
        top_bar.addStretch()
        top_bar.addWidget(self._log_out_button)
        layout.addLayout(top_bar)

        book_buttons = QHBoxLayout()
        self._add_book_button = QPushButton("Add Book")
        self._add_book_button.setObjectName("primary")
        self._add_book_button.clicked.connect(self._add_book)
        book_buttons.addWidget(self._add_book_button)

        self._edit_book_button = QPushButton("Edit Book")
        self._edit_book_button.clicked.connect(self._edit_book)
        book_buttons.addWidget(self._edit_book_button)

        book_buttons.addStretch()

        self._book_table = QTableWidget()
        self._book_table.setColumnCount(6)
        self._book_table.setHorizontalHeaderLabels(["Book ID", "Title", "Author", "Genre", "ISBN", "Year"])
        set_up_table(self._book_table, 1)

        books_tab = QWidget()
        books_layout = QVBoxLayout()
        books_layout.addLayout(book_buttons)
        books_layout.addWidget(self._book_table)
        books_tab.setLayout(books_layout)

        # one tab for each feature area
        tabs = QTabWidget()
        tabs.addTab(books_tab, "Books")
        self._loan_table = QTableWidget()
        self._loan_table.setColumnCount(7)
        self._loan_table.setHorizontalHeaderLabels(["Loan ID", "Borrower", "Title", "Copy ID","Loan Date", "Due Date", "Days Remaining"])
        # keep the loan ID hidden but available for loan actions
        self._loan_table.setColumnHidden(0, True)
        set_up_table(self._loan_table, 2)

        loans_tab = QWidget()
        loans_layout = QVBoxLayout()

        loan_buttons = QHBoxLayout()
        self._issue_loan_button = QPushButton("Issue Loan")
        self._issue_loan_button.setObjectName("primary")
        self._issue_loan_button.clicked.connect(self._issue_loan)
        loan_buttons.addWidget(self._issue_loan_button)

        self._return_button = QPushButton("Return")
        self._return_button.clicked.connect(self._return_loan)
        loan_buttons.addWidget(self._return_button)

        self._mark_lost_button = QPushButton("Mark Lost")
        self._mark_lost_button.setObjectName("danger")
        self._mark_lost_button.clicked.connect(self._mark_lost)
        loan_buttons.addWidget(self._mark_lost_button)

        loan_buttons.addStretch()

        loans_layout.addLayout(loan_buttons)
        loans_layout.addWidget(self._loan_table)

        loans_tab.setLayout(loans_layout)
        tabs.addTab(loans_tab, "Loans")

        self._overdue_table = QTableWidget()
        self._overdue_table.setColumnCount(6)
        self._overdue_table.setHorizontalHeaderLabels(["Borrower", "Title", "Copy ID", "Loan Date","Due Date", "Days Overdue"])
        set_up_table(self._overdue_table, 1)

        overdue_tab = QWidget()
        overdue_layout = QVBoxLayout()
        overdue_layout.addWidget(self._overdue_table)
        overdue_tab.setLayout(overdue_layout)
        tabs.addTab(overdue_tab, "Overdue")

        self._fine_table = QTableWidget()
        self._fine_table.setColumnCount(5)
        self._fine_table.setHorizontalHeaderLabels(["Fine ID", "Borrower", "Title", "Amount (PLN)","Date Issued"])
        self._fine_table.setColumnHidden(0, True)
        set_up_table(self._fine_table, 2)

        fines_tab = QWidget()
        fines_layout = QVBoxLayout()

        fine_buttons = QHBoxLayout()
        self._record_payment_button = QPushButton("Record Payment")
        self._record_payment_button.setObjectName("primary")
        self._record_payment_button.clicked.connect(self._record_payment)
        fine_buttons.addWidget(self._record_payment_button)
        fine_buttons.addStretch()

        fines_layout.addLayout(fine_buttons)
        fines_layout.addWidget(self._fine_table)
        fines_tab.setLayout(fines_layout)
        tabs.addTab(fines_tab, "Fines")

        self._audit_table = QTableWidget()
        self._audit_table.setColumnCount(5)
        self._audit_table.setHorizontalHeaderLabels(["Time", "Staff", "Action", "Table", "Record ID"])
        set_up_table(self._audit_table, 4)

        audit_tab = QWidget()
        audit_layout = QVBoxLayout()
        audit_layout.addWidget(self._audit_table)
        audit_tab.setLayout(audit_layout)
        self._audit_tab_index = tabs.addTab(audit_tab, "Audit Log")
        # refresh the audit log when opened to show the latest actions
        tabs.currentChanged.connect(self._tab_changed)

        layout.addWidget(tabs)

        # result of the last action, success or error
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        central_widget.setLayout(layout)

    def _log_out(self):
        self.logged_out = True
        self.close()

    def _load_books(self):
        # the whole table is refilled every time
        book_rows = books.get_all_books()
        self._book_table.setRowCount(len(book_rows))

        for row_index, book in enumerate(book_rows):
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
            borrower = f'{to_text(loan["last_name"])}, {to_text(loan["first_name"])}'

            self._loan_table.setItem(row_index, 0, QTableWidgetItem(to_text(loan["loan_id"])))
            self._loan_table.setItem(row_index, 1, QTableWidgetItem(borrower))
            self._loan_table.setItem(row_index, 2, QTableWidgetItem(to_text(loan["title"])))
            self._loan_table.setItem(row_index, 3, QTableWidgetItem(to_text(loan["copy_id"])))
            self._loan_table.setItem(row_index, 4, QTableWidgetItem(to_text(loan["checkout_date"])))
            self._loan_table.setItem(row_index, 5, QTableWidgetItem(to_text(loan["due_date"])))
            self._loan_table.setItem(row_index, 6, QTableWidgetItem(to_text(int(loan["days_remaining"]))))

        self._loan_table.resizeColumnsToContents()

    def _load_overdue(self):
        today = date.today().isoformat()
        overdue_rows = loans.get_overdue_loans(today)

        self._overdue_table.setRowCount(len(overdue_rows))

        for row_index, loan in enumerate(overdue_rows):
            borrower = f'{to_text(loan["last_name"])}, {to_text(loan["first_name"])}'

            self._overdue_table.setItem(row_index, 0, QTableWidgetItem(borrower))
            self._overdue_table.setItem(row_index, 1, QTableWidgetItem(to_text(loan["title"])))
            self._overdue_table.setItem(row_index, 2, QTableWidgetItem(to_text(loan["copy_id"])))
            self._overdue_table.setItem(row_index, 3, QTableWidgetItem(to_text(loan["checkout_date"])))
            self._overdue_table.setItem(row_index, 4, QTableWidgetItem(to_text(loan["due_date"])))
            self._overdue_table.setItem(row_index, 5, QTableWidgetItem(to_text(int(loan["days_overdue"]))))

        self._overdue_table.resizeColumnsToContents()

    def _load_fines(self):
        fine_rows = fines.get_unpaid_fines()
        self._fine_table.setRowCount(len(fine_rows))

        for row_index, fine in enumerate(fine_rows):
            borrower = f'{to_text(fine["last_name"])}, {to_text(fine["first_name"])}'

            self._fine_table.setItem(row_index, 0, QTableWidgetItem(to_text(fine["fine_id"])))
            self._fine_table.setItem(row_index, 1, QTableWidgetItem(borrower))
            self._fine_table.setItem(row_index, 2, QTableWidgetItem(to_text(fine["title"])))
            self._fine_table.setItem(row_index, 3, QTableWidgetItem(f'{fine["amount"]:.2f}'))
            self._fine_table.setItem(row_index, 4, QTableWidgetItem(to_text(fine["issued_date"])))

        self._fine_table.resizeColumnsToContents()

    def _tab_changed(self, index):
        if index == self._audit_tab_index:
            self._load_audit_log()

    def _load_audit_log(self):
        audit_rows = audit.get_audit_log()
        self._audit_table.setRowCount(len(audit_rows))

        for row_index, audit_row in enumerate(audit_rows):
            staff = f'{to_text(audit_row["last_name"])}, {to_text(audit_row["first_name"])}'

            self._audit_table.setItem(row_index, 0, QTableWidgetItem(to_text(audit_row["local_time"])))
            self._audit_table.setItem(row_index, 1, QTableWidgetItem(staff))
            self._audit_table.setItem(row_index, 2, QTableWidgetItem(to_text(audit_row["action"])))
            self._audit_table.setItem(row_index, 3, QTableWidgetItem(to_text(audit_row["table_name"])))
            self._audit_table.setItem(row_index, 4, QTableWidgetItem(to_text(audit_row["record_id"])))

        self._audit_table.resizeColumnsToContents()

    def _load_tables(self):
        self._load_loans()
        self._load_overdue()
        self._load_fines()

    def _add_book(self):
        self._status_label.setText("")

        dialog = BookDialog(self._librarian)

        # exec() blocks until the dialog closes and returns true only if it was accepted
        if dialog.exec():
            self._load_books()

    def _edit_book(self):
        self._status_label.setText("")

        row_index = get_selected_row(self._book_table)

        if row_index is None:
            self._status_label.setText("Select a book to edit.")
            return

        book_id = int(self._book_table.item(row_index, 0).text())

        dialog = BookDialog(self._librarian, books.get_book(book_id))

        if dialog.exec():
            self._load_books()

    def _issue_loan(self):
        self._status_label.setText("")

        dialog = IssueLoanDialog(self._librarian)

        if dialog.exec():
            self._load_tables()
            self._status_label.setText(dialog.get_message())

    def _return_loan(self):
        self._status_label.setText("")

        row_index = get_selected_row(self._loan_table)

        if row_index is None:
            self._status_label.setText("Select a loan first.")
            return

        loan_id = int(self._loan_table.item(row_index, 0).text())
        borrower = self._loan_table.item(row_index, 1).text()
        title = self._loan_table.item(row_index, 2).text()

        # default set to no to prevent accidental returns
        answer = QMessageBox.question(
            self,
            "Return Loan",
            f"Return '{title}' borrowed by {borrower}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if answer != QMessageBox.StandardButton.Yes:
            return

        today = date.today().isoformat()

        try:
            days_late, fine_amount = loans.return_loan(loan_id, self._librarian.get_user_id(), today)
        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self._load_tables()

        message = f"Returned '{title}'. Days late: {days_late}."
        if fine_amount > 0:
            message += f" Fine: {fine_amount:.2f} PLN."

        self._status_label.setText(message)

    def _mark_lost(self):
        self._status_label.setText("")

        row_index = get_selected_row(self._loan_table)

        if row_index is None:
            self._status_label.setText("Select a loan first.")
            return

        loan_id = int(self._loan_table.item(row_index, 0).text())
        borrower = self._loan_table.item(row_index, 1).text()
        title = self._loan_table.item(row_index, 2).text()

        answer = QMessageBox.question(
            self,
            "Mark Lost",
            f"Mark '{title}' borrowed by {borrower} as lost?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if answer != QMessageBox.StandardButton.Yes:
            return

        today = date.today().isoformat()

        try:
            fine_amount = loans.mark_lost(loan_id, self._librarian.get_user_id(), today)
        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self._load_tables()
        self._status_label.setText(f"'{title}' marked as lost. Fine: {fine_amount:.2f} PLN.")

    def _record_payment(self):
        self._status_label.setText("")

        row_index = get_selected_row(self._fine_table)

        if row_index is None:
            self._status_label.setText("Select a fine first.")
            return

        fine_id = int(self._fine_table.item(row_index, 0).text())
        borrower = self._fine_table.item(row_index, 1).text()
        amount = self._fine_table.item(row_index, 3).text()

        answer = QMessageBox.question(
            self,
            "Record Payment",
            f"Record payment of {amount} PLN from {borrower}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if answer != QMessageBox.StandardButton.Yes:
            return

        today = date.today().isoformat()

        try:
            fines.record_payment(fine_id, self._librarian.get_user_id(), today)
        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self._load_tables()
        self._status_label.setText(f"Payment of {amount} PLN recorded for {borrower}.")
