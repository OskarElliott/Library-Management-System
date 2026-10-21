
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget

REQUIRED_MARK = " <font color='#B42318'>*</font>"

def to_text(value): # null from the database arrives as none, which no widget can display
    if value is None:
        return ""
    return str(value)

def set_up_table(table, stretch_column):
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(32)

    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    table.horizontalHeader().setSectionResizeMode(stretch_column, QHeaderView.ResizeMode.Stretch)

    table.setShowGrid(False)
