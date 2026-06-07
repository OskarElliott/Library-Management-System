import sys

from PySide6.QtWidgets import QApplication, QDialog

from db.connection import get_connection
from services.auth_service import AuthService
from ui.login_window import LoginDialog
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    conn = get_connection()
    auth = AuthService(conn)

    login = LoginDialog(auth)
    if login.exec() != QDialog.Accepted:
        return

    window = MainWindow(login.user, conn)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()