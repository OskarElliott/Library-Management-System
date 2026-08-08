from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from services import auth

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__() 

        self._librarian = None
        self._setup_ui()

    def _setup_ui(self): 
        self.setWindowTitle("Library System Login")
        self.resize(400, 300)

        layout = QVBoxLayout()

        title = QLabel("<b>Library System Login</b>")
        layout.addWidget(title)

        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #333366;")
        layout.addWidget(username_label)

        self._username_input = QLineEdit()
        layout.addWidget(self._username_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #333366;")
        layout.addWidget(password_label)
        
        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._password_input)

        self._toggle_box = QCheckBox("Show Password")
        self._toggle_box.toggled.connect(self._toggle_password_view)
        layout.addWidget(self._toggle_box)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #C62828")
        layout.addWidget(self._error_label)

        self._login_button = QPushButton("Login")
        self._login_button.clicked.connect(self._login)
        self._login_button.setStyleSheet("color: #3B82F6")
        layout.addWidget(self._login_button)
    
        self.setLayout(layout)

    def _toggle_password_view(self, checked):
        if checked:
            self._password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self._password_input.setEchoMode(QLineEdit.EchoMode.Password)


    def _login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text()

        if username == "" or password == "":
            self._error_label.setText("<b>Please enter a username and password</b>")
            return

        librarian = auth.login(username, password)

        if librarian is None:
            self._error_label.setText("<b>Invalid username or password</b>")
            return

        self._librarian = librarian
        self.accept()

    def get_librarian(self):
        return self._librarian
