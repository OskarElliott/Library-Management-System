from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui import style

app = QApplication([])
app.setStyle("Fusion")
app.setStyleSheet(style.STYLESHEET)

# the loop brings back the login window after log out
while True:
    login = LoginWindow()

    if not login.exec():
        break

    librarian = login.get_librarian()
    window = MainWindow(librarian)
    window.show()

    app.exec()

    if not window.logged_out:
        break
    

