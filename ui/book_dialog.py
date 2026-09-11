from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
from services import books
from ui.formatting import to_text

class BookDialog(QDialog):
    def __init__(self, librarian, book=None):
        super().__init__() # allows access to methods and proper titles of qdialog

        self._librarian = librarian
        self._book = book  # none means that a new book is being added

        self._setup_ui()

        if self._book is not None:
            self._load_book()
            self._load_copies()

    def _setup_ui(self):
        if self._book is None:
            self.setWindowTitle("Add Book")
        else:
            self.setWindowTitle("Edit Book")

        layout = QVBoxLayout()

        #one label and one input per row
        form = QFormLayout()
        self._title_field = QLineEdit()
        self._first_name_field = QLineEdit()
        self._last_name_field = QLineEdit()
        self._genre_box = QComboBox()
        self._isbn_field = QLineEdit()
        self._publisher_field = QLineEdit()
        self._year_field = QLineEdit()

        form.addRow("Title", self._title_field)
        form.addRow("Author first name", self._first_name_field)
        form.addRow("Author last name", self._last_name_field)
        form.addRow("Genre", self._genre_box)
        form.addRow("ISBN", self._isbn_field)
        form.addRow("Publisher", self._publisher_field)
        form.addRow("Year", self._year_field)

        #copies are chosen when the book is added and only counted afterwards
        if self._book is None:
            self._copies_box = QSpinBox()
            self._copies_box.setMinimum(1)
            self._copies_box.setMaximum(20)
            form.addRow("Number of copies", self._copies_box)
        else:
            copies_layout = QVBoxLayout()

            self._copies_table = QTableWidget()
            self._copies_table.setColumnCount(4)
            self._copies_table.setHorizontalHeaderLabels(["Copy ID", "Purchase Date", "Condition", "Status"])
            self._copies_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self._copies_table.setSelectionBehavior(QTableWidget.SelectRows)

            copies_layout.addWidget(self._copies_table)

            self._add_copy_button = QPushButton("Add Copy")
            self._discard_copy_button = QPushButton("Discard Copy")

            copy_buttons = QHBoxLayout()
            copy_buttons.addWidget(self._add_copy_button)
            copy_buttons.addWidget(self._discard_copy_button)
            copies_layout.addLayout(copy_buttons)

            layout.addLayout(copies_layout)

            self._add_copy_button.clicked.connect(self._add_copy)
            self._discard_copy_button.clicked.connect(self._discard_copy)

        layout.addLayout(form)

        # the genre list comes from the db, so the same genre cannot be spelt in different ways
        # each item shows the name and carries the genre_id with it

        self._genre_box.addItem("-- Select Genre --", None)
        for genre in books.get_all_genres():
            self._genre_box.addItem(genre["name"], genre["genre_id"])

        # shows errors raised by the buttons
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        buttons = QHBoxLayout()
        self._withdraw_button = QPushButton("Withdraw Book")
        self._cancel_button = QPushButton("Cancel")
        self._save_button = QPushButton("Save")
        buttons.addWidget(self._withdraw_button)
        buttons.addStretch()
        buttons.addWidget(self._cancel_button)
        buttons.addWidget(self._save_button)
        layout.addLayout(buttons)

        self._cancel_button.clicked.connect(self.reject)
        self._save_button.clicked.connect(self._save)
        self._withdraw_button.clicked.connect(self._withdraw)

        # there is nothing to withdraw when the book does not exist
        if self._book is None:
            self._withdraw_button.setVisible(False)

        self.setLayout(layout)

    def _save(self):
        self._status_label.setText("")

        isbn = self._isbn_field.text()
        title = self._title_field.text()
        genre_id = self._genre_box.currentData()
        publication_year = self._year_field.text()
        publisher = self._publisher_field.text()
        author_first_name = self._first_name_field.text()
        author_last_name = self._last_name_field.text()

        try:
            if self._book is None:
                book_id = books.add_book(isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name, self._librarian.get_user_id())

                for i in range (self._copies_box.value()):
                    books.add_copy(book_id, self._librarian.get_user_id())

            else: 
                books.edit_book(self._book["book_id"], isbn, title, genre_id, publication_year, publisher, author_first_name, author_last_name, self._librarian.get_user_id())

        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self.accept()

    def _withdraw(self):
        answer = QMessageBox.question(self, "Withdraw Book", "Are you sure you want to withdraw this book?\nAll copies will be discarded.",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            books.withdraw_book(self._book["book_id"], self._librarian.get_user_id())

        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self.accept()

    def _load_book(self):
        self._title_field.setText(to_text(self._book["title"]))
        self._first_name_field.setText(to_text(self._book["first_name"]))
        self._last_name_field.setText(to_text(self._book["last_name"]))
        self._isbn_field.setText(to_text(self._book["isbn"]))
        self._publisher_field.setText(to_text(self._book["publisher"]))
        self._year_field.setText(to_text(self._book["publication_year"]))

        # findData finds the item carrying the books genre_id and
        # a book with no genre lands on the placeholder which carries none

        self._genre_box.setCurrentIndex(self._genre_box.findData(self._book["genre_id"]))

    def _load_copies(self):
        copy_rows = books.get_copies(self._book["book_id"])

        self._copies_table.setRowCount(len(copy_rows))

        for row_index, copy in enumerate(copy_rows):
            self._copies_table.setItem(row_index, 0, QTableWidgetItem(str(copy["copy_id"])))
            self._copies_table.setItem(row_index, 1, QTableWidgetItem(to_text(copy["purchase_date"])))
            self._copies_table.setItem(row_index, 2, QTableWidgetItem(to_text(copy["condition"])))
            self._copies_table.setItem(row_index, 3, QTableWidgetItem(to_text(copy["status"])))

        self._copies_table.resizeColumnsToContents()

    def _add_copy(self):
        self._status_label.setText("")

        try:
            books.add_copy(self._book["book_id"], self._librarian.get_user_id())

        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self._load_copies()

    def _discard_copy(self):
        self._status_label.setText("")

        row_index = self._copies_table.currentRow()

        if row_index == -1:
            self._status_label.setText("Select a copy to discard.")
            return

        copy_id = int(self._copies_table.item(row_index, 0).text())

        try:
            books.discard_copy(copy_id, self._librarian.get_user_id())

        except ValueError as error:
            self._status_label.setText(str(error))
            return

        self._load_copies()