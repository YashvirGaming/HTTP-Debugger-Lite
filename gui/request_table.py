from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableWidget,
    QMenu,
    QHeaderView,
)

from core.models import SessionRecord
from utils.helpers import make_item, method_color, qcenter, status_color


class RequestTable(QTableWidget):
    HEADERS = ["#", "Method", "Status", "URL", "Type", "Size", "Duration"]

    def __init__(self, signals, parent=None):
        super().__init__(0, len(self.HEADERS), parent)
        self.signals = signals
        self.sessions: list[SessionRecord] = []

        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)

        self.setColumnWidth(0, 55)    #
        self.setColumnWidth(1, 90)    # Method
        self.setColumnWidth(2, 85)    # Status
        self.setColumnWidth(3, 600)   # 🔥 URL (BIG)
        self.setColumnWidth(4, 90)    # Type
        self.setColumnWidth(5, 90)    # Size
        self.setColumnWidth(6, 90)    # Duration
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.itemSelectionChanged.connect(self._emit_selected)

    def load_sessions(self, sessions: list[SessionRecord]) -> None:
        self.sessions = sessions
        self.setRowCount(0)
        align = qcenter()

        for session in sessions:
            row = self.rowCount()
            self.insertRow(row)

            id_item = make_item(str(session.id), align)

            method_item = make_item(session.method, align)

            # ✅ MUST BE INSIDE LOOP
            if session.method == "TLS":
                from PySide6.QtGui import QColor
                method_item.setForeground(QColor("#a855f7"))  # purple
            else:
                method_item.setForeground(method_color(session.method))

            status_item = make_item(str(session.status or "-"), align)
            status_item.setForeground(status_color(session.status))

            display_url = session.url or session.host or ""

            if len(display_url) > 60:
                display_url = display_url[:60] + "..."

            url_item = make_item(display_url)
            url_item.setToolTip(session.url or session.host or "")

            type_text = (session.type or "").upper()
            type_item = make_item(type_text, align)

            size_item = make_item(session.size_text, align)
            duration_item = make_item(session.duration_text, align)

            self.setItem(row, 0, id_item)
            self.setItem(row, 1, method_item)
            self.setItem(row, 2, status_item)
            self.setItem(row, 3, url_item)
            self.setItem(row, 4, type_item)
            self.setItem(row, 5, size_item)
            self.setItem(row, 6, duration_item)

        if self.rowCount() > 0:
            self.selectRow(0)

    def _emit_selected(self) -> None:
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        if 0 <= row < len(self.sessions):
            self.signals.request_selected.emit(self.sessions[row].id)

    def _show_context_menu(self, position):
        indexes = self.selectedIndexes()
        if not indexes:
            return

        menu = QMenu()

        copy_action = QAction("Copy URL")
        copy_full_row = QAction("Copy Row")

        menu.addAction(copy_action)
        menu.addAction(copy_full_row)

        action = menu.exec(QCursor.pos())

        row = indexes[0].row()

        if action == copy_action:
            url_item = self.item(row, 3)
            if url_item:
                QGuiApplication.clipboard().setText(url_item.text())

        elif action == copy_full_row:
            values = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    values.append(item.text())
            QGuiApplication.clipboard().setText(" | ".join(values))
