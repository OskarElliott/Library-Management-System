from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

app = QApplication([])
login = LoginWindow()

if login.exec():
    librarian = login.get_librarian()

    window = MainWindow(librarian)
    window.show()

    app.exec()