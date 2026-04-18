import base64
import html
import json

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

from core.formatter import pretty_json
from core.highlighter import JsonHighlighter
from core.models import SessionRecord


class ResponseTabs(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PaneFrame")
        self.current_session = None
        self.current_image_bytes = None
        self.current_image_type = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        top_bar = QHBoxLayout()

        title = QLabel("Response Details")
        title.setObjectName("SectionTitle")

        self.meta_label = QLabel("Type: - | Size: 0 B")
        self.meta_label.setObjectName("SubTitleLabel")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search current tab...")

        self.copy_btn = QPushButton("Copy")
        self.open_btn = QPushButton("Open URL")
        self.save_btn = QPushButton("Save Image")

        self.search_box.textChanged.connect(self.search_current)
        self.copy_btn.clicked.connect(self.copy_current)
        self.open_btn.clicked.connect(self.open_url)
        self.save_btn.clicked.connect(self.save_image)

        top_bar.addWidget(title)
        top_bar.addWidget(self.meta_label)
        top_bar.addStretch()
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.open_btn)
        top_bar.addWidget(self.save_btn)

        layout.addLayout(top_bar)

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
        self.tabs.addTab(self.html_view, "Preview")

        layout.addWidget(self.tabs)

        self.save_btn.setEnabled(False)

    def update_data(self, session: SessionRecord | None) -> None:
        self.current_session = session
        self.current_image_bytes = None
        self.current_image_type = ""
        self.save_btn.setEnabled(False)

        if session is None:
            self.header_view.setPlainText("")
            self.content_view.setPlainText("")
            self.raw_view.setPlainText("")
            self.meta_label.setText("Type: - | Size: 0 B")
            self.html_view.setHtml(
                "<html><body style='background:#0b1020;color:white;font-family:Consolas;'><pre>No preview loaded.</pre></body></html>"
            )
            return

        headers = "\n".join(f"{k}: {v}" for k, v in (session.response_headers or {}).items())
        self.header_view.setPlainText(headers)

        formatted = pretty_json(session.response_body)
        self.content_view.setPlainText(formatted)

        self.raw_view.setPlainText(session.response_body or "")

        content_type = (session.type or "").lower()
        body = session.response_body or ""
        size_bytes = len(body.encode("utf-8", errors="ignore")) if isinstance(body, str) else len(body or b"")
        self.meta_label.setText(f"Type: {content_type or '-'} | Size: {self._format_size(size_bytes)}")

        def json_to_html(obj, path="root"):
            if isinstance(obj, dict):
                items = ""
                for i, (k, v) in enumerate(obj.items()):
                    child_id = f"{path}_{i}"
                    items += f"""
                    <li>
                        <span class="toggle" onclick="toggle('{child_id}', this)">▶</span>
                        <span class="key">{html.escape(str(k))}</span>:
                        <div id="{child_id}" class="hidden">{json_to_html(v, child_id)}</div>
                    </li>
                    """
                return f"<ul>{items}</ul>"
            if isinstance(obj, list):
                items = ""
                for i, v in enumerate(obj):
                    child_id = f"{path}_{i}"
                    items += f"""
                    <li>
                        <span class="toggle" onclick="toggle('{child_id}', this)">▶</span>
                        <span class="index">[{i}]</span>
                        <div id="{child_id}" class="hidden">{json_to_html(v, child_id)}</div>
                    </li>
                    """
                return f"<ul>{items}</ul>"
            return f"<span class='value'>{html.escape(str(obj))}</span>"

        is_image = any(t in content_type for t in ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif", "image/bmp"])
        is_html = "html" in content_type or "<html" in body.lower() or "<!doctype html" in body.lower()
        is_json = "application/json" in content_type or "text/json" in content_type

        if is_image and body:
            try:
                raw = session.response_body.encode("latin1", errors="ignore") if isinstance(session.response_body, str) else session.response_body
                self.current_image_bytes = raw
                self.current_image_type = content_type
                self.save_btn.setEnabled(True)
                b64 = base64.b64encode(raw).decode()
                self.html_view.setHtml(
                    f"""
                    <html>
                    <body style="margin:0;background:#0b1020;display:flex;justify-content:center;align-items:center;height:100vh;">
                        <img src="data:{content_type};base64,{b64}" style="max-width:96%;max-height:96%;border-radius:12px;box-shadow:0 0 25px rgba(0,0,0,.45);" />
                    </body>
                    </html>
                    """
                )
                return
            except Exception:
                self.html_view.setHtml(
                    "<html><body style='background:#0b1020;color:white;font-family:Consolas;'><pre>Failed to render image.</pre></body></html>"
                )
                return

        if is_json and body.strip():
            try:
                parsed = json.loads(body)
                tree_html = json_to_html(parsed)
                self.html_view.setHtml(
                    f"""
                    <html>
                    <head>
                    <style>
                        body {{ background:#0b1020;color:#00ffcc;font-family:Consolas;padding:10px; }}
                        ul {{ list-style:none; margin-left:15px; padding-left:15px; border-left:1px solid #1f2937; }}
                        .key {{ color:#60a5fa; }}
                        .value {{ color:#34d399; }}
                        .index {{ color:#facc15; }}
                        .toggle {{ cursor:pointer;color:#f87171;margin-right:6px;user-select:none; }}
                        .hidden {{ display:none; margin-left:10px; }}
                        #searchBox {{ width:100%;padding:8px;margin-bottom:10px;background:#020617;color:#00ffcc;border:1px solid #1f2937;border-radius:8px;box-sizing:border-box; }}
                        mark {{ background:#facc15;color:black;padding:0 2px;border-radius:2px; }}
                        h3 {{ margin-top:0; }}
                    </style>
                    <script>
                        function toggle(id, el) {{
                            var node = document.getElementById(id);
                            var open = node.style.display === "block";
                            node.style.display = open ? "none" : "block";
                            if (el) el.textContent = open ? "▶" : "▼";
                        }}

                        function clearMarks(root) {{
                            root.querySelectorAll("mark").forEach(function(mark) {{
                                const text = document.createTextNode(mark.textContent);
                                mark.parentNode.replaceChild(text, mark);
                            }});
                        }}

                        function highlightNode(node, query) {{
                            if (!query) return;
                            if (node.nodeType === 3) {{
                                const text = node.nodeValue;
                                const lower = text.toLowerCase();
                                const q = query.toLowerCase();
                                const index = lower.indexOf(q);
                                if (index >= 0) {{
                                    const span = document.createElement("span");
                                    span.innerHTML =
                                        text.substring(0, index) +
                                        "<mark>" + text.substring(index, index + query.length) + "</mark>" +
                                        text.substring(index + query.length);
                                    node.parentNode.replaceChild(span, node);
                                }}
                            }} else {{
                                Array.from(node.childNodes).forEach(child => highlightNode(child, query));
                            }}
                        }}

                        function searchText() {{
                            const input = document.getElementById("searchBox").value.trim();
                            const root = document.getElementById("treeRoot");
                            clearMarks(root);
                            if (!input) return;
                            highlightNode(root, input);
                        }}
                    </script>
                    </head>
                    <body>
                        <input id="searchBox" placeholder="Search JSON..." onkeyup="searchText()" />
                        <h3>JSON Tree</h3>
                        <div id="treeRoot">{tree_html}</div>
                    </body>
                    </html>
                    """
                )
                return
            except Exception:
                pass

        if is_html and body.strip():
            try:
                self.html_view.setHtml(body, QUrl(session.url or ""))
                return
            except Exception:
                self.html_view.setHtml(
                    "<html><body style='background:#0b1020;color:white;font-family:Consolas;'><pre>Failed to render HTML.</pre></body></html>"
                )
                return

        preview = body[:12000] if body else "No response body."
        self.html_view.setHtml(
            f"""
            <html>
            <head>
            <style>
                body {{ background:#0b1020;color:#00ffcc;font-family:Consolas;padding:10px; }}
                #searchBox {{ width:100%;padding:8px;margin-bottom:10px;background:#020617;color:#00ffcc;border:1px solid #1f2937;border-radius:8px;box-sizing:border-box; }}
                mark {{ background:#facc15;color:black;padding:0 2px;border-radius:2px; }}
                pre {{ white-space:pre-wrap;word-wrap:break-word; }}
            </style>
            <script>
                function searchRaw() {{
                    const input = document.getElementById("searchBox").value;
                    const content = document.getElementById("content");
                    const original = content.getAttribute("data-original");
                    if (!input) {{
                        content.innerHTML = original;
                        return;
                    }}
                    const escaped = input.replace(/[.*+?^${{}}()|[\]\\]/g, '\\\\$&');
                    const regex = new RegExp(escaped, "gi");
                    content.innerHTML = original.replace(regex, function(match) {{
                        return "<mark>" + match + "</mark>";
                    }});
                }}
            </script>
            </head>
            <body>
                <input id="searchBox" placeholder="Search preview..." onkeyup="searchRaw()" />
                <pre id="content" data-original="{html.escape(preview)}">{html.escape(preview)}</pre>
            </body>
            </html>
            """
        )

    def copy_current(self) -> None:
        current = self.tabs.currentWidget()

        if current is self.header_view:
            QApplication.clipboard().setText(self.header_view.toPlainText())
            return

        if current is self.content_view:
            QApplication.clipboard().setText(self.content_view.toPlainText())
            return

        if current is self.raw_view:
            QApplication.clipboard().setText(self.raw_view.toPlainText())
            return

        if self.current_session and self.current_session.response_body:
            QApplication.clipboard().setText(str(self.current_session.response_body))
            return

        QApplication.clipboard().setText("")

    def search_current(self, text: str) -> None:
        current = self.tabs.currentWidget()

        if current in (self.header_view, self.content_view, self.raw_view):
            if not text:
                return
            cursor = current.document().find(text)
            if not cursor.isNull():
                current.setTextCursor(cursor)

    def open_url(self) -> None:
        if self.current_session and self.current_session.url:
            QDesktopServices.openUrl(QUrl(self.current_session.url))

    def save_image(self) -> None:
        if not self.current_image_bytes:
            return

        ext = "bin"
        if "/" in self.current_image_type:
            ext = self.current_image_type.split("/")[-1].replace("jpeg", "jpg")

        path, _ = QFileDialog.getSaveFileName(self, "Save Image", f"response_image.{ext}", f"Image Files (*.{ext});;All Files (*)")
        if not path:
            return

        with open(path, "wb") as f:
            f.write(self.current_image_bytes)

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        return f"{size / (1024 * 1024):.2f} MB"