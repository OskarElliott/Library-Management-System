from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget

REQUIRED_MARK = " <font color='#B42318'>*</font>"

# convert none to empty text and integers to strings for table cells
def to_text(value):
    if value is None:
        return ""
    return str(value)

def set_up_table(table, stretch_column):
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(32)

    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    table.horizontalHeader().setSectionResizeMode(stretch_column, QHeaderView.ResizeMode.Stretch)

    table.setShowGrid(False)

# use selected rows to detect whether a row is actually selected
def get_selected_row(table):
    selected_rows = table.selectionModel().selectedRows()

    if not selected_rows:
        return None

    return selected_rows[0].row()
