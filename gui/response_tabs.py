from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QTabWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

from core.formatter import make_preview_text, pretty_json
from core.highlighter import JsonHighlighter
from core.models import SessionRecord


class ResponseTabs(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PaneFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Response Details")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        self.header_view = QPlainTextEdit()
        self.content_view = QPlainTextEdit()
        self.raw_view = QPlainTextEdit()
        self.html_view = QWebEngineView()

        for widget in (self.header_view, self.content_view, self.raw_view):
            widget.setReadOnly(True)
            widget.setFont(QFont("Consolas", 10))

        self.content_highlighter = JsonHighlighter(self.content_view.document())

        self.tabs.addTab(self.header_view, "Header")
        self.tabs.addTab(self.content_view, "Content")
        self.tabs.addTab(self.raw_view, "Raw")
        self.tabs.addTab(self.html_view, "HTML")

        layout.addWidget(self.tabs)

    def update_data(self, session: SessionRecord | None) -> None:
        if session is None:
            self.header_view.setPlainText("")
            self.content_view.setPlainText("")
            self.raw_view.setPlainText("")
            self.html_view.setHtml("<html><body style='background:#0b1020;color:white;'><pre>No HTML loaded.</pre></body></html>")
            return

        headers = "\n".join(f"{k}: {v}" for k, v in (session.response_headers or {}).items())
        self.header_view.setPlainText(headers)

        formatted = pretty_json(session.response_body)
        self.content_view.setPlainText(formatted)

        self.raw_view.setPlainText(session.response_body or "")

        content_type = (session.type or "").lower()
        body = session.response_body or ""

        if "html" in content_type and body.strip():
            base_url = QUrl(session.url or "")
            self.html_view.setHtml(body, base_url)
        else:
            self.html_view.setHtml(
                "<html><body style='background:#0b1020;color:white;font-family:Consolas;'>"
                "<pre>No HTML preview for this response.</pre>"
                "</body></html>"
            )