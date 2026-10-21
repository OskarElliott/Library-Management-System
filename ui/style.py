STYLESHEET = """
QWidget {
    color: #1F2937;
}

QMainWindow, QDialog {
    background-color: #F5F6F8;
}

QLabel {
    background-color: transparent;
}

QLineEdit, QComboBox, QSpinBox, QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D5DD;
    border-radius: 6px;
    padding: 5px 8px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QListWidget:focus {
    border: 1px solid #2563EB;
}

QListWidget::item:selected {
    background-color: #E0EAFF;
    color: #1F2937;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D0D5DD;
    border-radius: 6px;
    padding: 6px 14px;
}

QPushButton:hover {
    background-color: #F3F4F6;
}

QPushButton:pressed {
    background-color: #E5E7EB;
}

QPushButton:disabled {
    color: #9CA3AF;
    background-color: #F3F4F6;
    border-color: #E5E7EB;
}

QPushButton#primary {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #2563EB;
}

QPushButton#primary:hover {
    background-color: #1D4ED8;
    border-color: #1D4ED8;
}

QPushButton#primary:disabled {
    background-color: #93B4F5;
    border-color: #93B4F5;
    color: #FFFFFF;
}

QPushButton#danger {
    color: #B42318;
    border: 1px solid #F1B5AE;
}

QPushButton#danger:hover {
    background-color: #FEF3F2;
}

QMessageBox QPushButton:default {
    border: 2px solid #2563EB;
}

QTabWidget::pane {
    border: none;
    border-top: 1px solid #D0D5DD;
}

QTabBar::tab {
    background-color: transparent;
    border: none;
    padding: 8px 14px;
    color: #6B7280;
}

QTabBar::tab:hover {
    color: #1F2937;
}

QTabBar::tab:selected {
    color: #1F2937;
    border-bottom: 2px solid #2563EB;
    font-weight: 600;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D5DD;
    border-radius: 6px;
    outline: 0;
}

QTableWidget::item {
    border-bottom: 1px solid #EEF0F3;
    padding: 4px 8px;
}

QTableWidget::item:hover {
    background-color: #F3F6FB;
}

QTableWidget::item:selected {
    background-color: #E0EAFF;
    color: #1F2937;
}

QHeaderView::section {
    background-color: #F9FAFB;
    border: none;
    border-bottom: 1px solid #D0D5DD;
    padding: 6px 8px;
    font-weight: 600;
    color: #374151;
}

"""

ERROR_STYLE = "color: #B42318"
