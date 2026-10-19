
STYLESHEET = """
QWidget {
    color: #1A1A1A;
}

QMainWindow, QDialog {
    background-color: #F0F0F0;
    font-family: "Inter", "Segoe UI", Arial;
}

QLabel {
    background-color: transparent;
}

QLineEdit, QComboBox, QSpinBox, QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #8C8C8C;
    border-radius: 0;
    padding: 3px;
}

QPushButton {
    background-color: #ECECEC;
    border: 1px solid #8C8C8C;
    border-radius: 0;
    padding: 4px 14px;
}

QPushButton:pressed {
    background-color: #DADADA;
}

QPushButton:hover {
    background-color: #E0E0E0;
}

QPushButton:disabled {
    color: #8C8C8C;
    background-color: #F0F0F0;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #0078D6;
}

QMessageBox QPushButton:default {
    border: 2px solid #0078D6;
}

QTabWidget::pane {
    border: 1px solid #8C8C8C;
    background-color: #F0F0F0;
}

QTabBar::tab {
    background-color: #DADADA;
    border: 1px solid #8C8C8C;
    padding: 4px 12px;
}

QTabBar::tab:selected {
    background-color: #F0F0F0;
    border-bottom-color: #F0F0F0;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #8C8C8C;
}

QTableWidget::item {
    border-bottom: 1px solid #E0E0E0;
    padding: 2px 4px;
}

QTableWidget::item:selected {
    background-color: #CCE4F7;
    color: #1A1A1A;
}

QHeaderView::section {
    background-color: #E8E8E8;
    border: none;
    border-right: 1px solid #8C8C8C;
    border-bottom: 1px solid #8C8C8C;
    padding: 3px 4px;
    font-weight: 600;
}
"""

ERROR_STYLE = "color: #BF0000"
