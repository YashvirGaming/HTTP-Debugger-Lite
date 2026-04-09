from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QTabWidget, QVBoxLayout

from core.formatter import make_preview_text, pretty_json
from core.highlighter import JsonHighlighter
from core.models import SessionRecord


class RequestTabs(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PaneFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Request Details")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.header_view = QPlainTextEdit()
        self.content_view = QPlainTextEdit()
        self.raw_view = QPlainTextEdit()

        for widget in (self.header_view, self.content_view, self.raw_view):
            widget.setReadOnly(True)
            widget.setFont(QFont("Consolas", 10))

        self.content_highlighter = JsonHighlighter(self.content_view.document())

        self.tabs.addTab(self.header_view, "Header")
        self.tabs.addTab(self.content_view, "Content")
        self.tabs.addTab(self.raw_view, "Raw")
        layout.addWidget(self.tabs)

    def update_data(self, session: SessionRecord | None) -> None:
        if session is None:
            self.header_view.setPlainText("")
            self.content_view.setPlainText("")
            self.raw_view.setPlainText("")
            return
        headers = "\n".join(f"{k}: {v}" for k, v in (session.request_headers or {}).items())
        self.header_view.setPlainText(headers)
        formatted = pretty_json(session.request_body)
        self.content_view.setPlainText(formatted)
        raw = f"{session.method} {session.url}\n\n{session.request_body}"
        self.raw_view.setPlainText(make_preview_text(raw))
