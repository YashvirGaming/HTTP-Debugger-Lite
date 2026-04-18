from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QFrame, QLabel, QPlainTextEdit, QTabWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
)

from core.formatter import make_preview_text, pretty_json
from core.models import SessionRecord

import json


class RequestTabs(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PaneFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        top_bar = QHBoxLayout()
        self.title = QLabel("Request Details")
        self.title.setObjectName("SectionTitle")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.search_text)

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy_current)

        self.open_btn = QPushButton("Open URL")
        self.open_btn.clicked.connect(self.open_url)

        top_bar.addWidget(self.title)
        top_bar.addStretch()
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.open_btn)

        layout.addLayout(top_bar)

        self.tabs = QTabWidget()

        self.header_view = QPlainTextEdit()
        self.content_view = QPlainTextEdit()
        self.raw_view = QPlainTextEdit()

        for widget in (self.header_view, self.content_view, self.raw_view):
            widget.setReadOnly(True)
            widget.setFont(QFont("Consolas", 10))

        self.tabs.addTab(self.header_view, "Header")
        self.tabs.addTab(self.content_view, "Content")
        self.tabs.addTab(self.raw_view, "Raw")

        layout.addWidget(self.tabs)

        self.current_session = None

    def update_data(self, session: SessionRecord | None) -> None:
        self.current_session = session

        if session is None:
            self.header_view.setPlainText("")
            self.content_view.setPlainText("")
            self.raw_view.setPlainText("")
            return

        headers = "\n".join(f"{k}: {v}" for k, v in (session.request_headers or {}).items())
        self.header_view.setPlainText(headers)

        body = session.request_body or ""

        try:
            parsed = json.loads(body)
            formatted = json.dumps(parsed, indent=2)
        except:
            formatted = body

        self.content_view.setPlainText(formatted)

        raw = f"{session.method} {session.url}\n\n{session.request_body}"
        self.raw_view.setPlainText(make_preview_text(raw))

    def copy_current(self):
        current_widget = self.tabs.currentWidget()
        text = current_widget.toPlainText()
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def open_url(self):
        if self.current_session and self.current_session.url:
            QDesktopServices.openUrl(QUrl(self.current_session.url))

    def search_text(self, text):
        if not text:
            return

        current_widget = self.tabs.currentWidget()
        cursor = current_widget.textCursor()
        document = current_widget.document()

        cursor = document.find(text)
        if cursor:
            current_widget.setTextCursor(cursor)