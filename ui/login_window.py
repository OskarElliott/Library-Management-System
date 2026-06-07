from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QLabel, QFormLayout, QVBoxLayout

class LoginDialog(QDialog):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.user = None
        
        self.setWindowTitle("Library Login")

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")

        login_button = QPushButton("Log in")
        login_button.setDefault(True)
        login_button.clicked.connect(self._attempt_login)

        form = QFormLayout()
        form.addRow("Username", self.username_input)
        form.addRow("Password", self.password_input)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(login_button)
        self.setLayout(layout)

    def _attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        user = self.auth_service.login(username, password)
        if user is None:
            self.error_label.setText("Incorrect username/password")
            return
        
        self.user = user
        self.accept()

