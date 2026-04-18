import re

from PySide6.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#60a5fa"))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22c55e"))

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#f59e0b"))

        self.bool_format = QTextCharFormat()
        self.bool_format.setForeground(QColor("#ef4444"))

        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#f472b6"))

        self.brace_format = QTextCharFormat()
        self.brace_format.setForeground(QColor("#c084fc"))

        self.url_format = QTextCharFormat()
        self.url_format.setForeground(QColor("#38bdf8"))

        self.header_key_format = QTextCharFormat()
        self.header_key_format.setForeground(QColor("#a78bfa"))

        self.rules = [
            (re.compile(r'"([^"\\]|\\.)*"\s*:'), self.key_format),
            (re.compile(r':\s*"([^"\\]|\\.)*"'), self.string_format),
            (re.compile(r'\b-?\d+(\.\d+)?\b'), self.number_format),
            (re.compile(r'\b(true|false)\b'), self.bool_format),
            (re.compile(r'\bnull\b'), self.null_format),
            (re.compile(r'[\{\}\[\]]'), self.brace_format),
            (re.compile(r'https?://[^\s"\']+'), self.url_format),
            (re.compile(r'^[A-Za-z0-9\-]+(?=:\s)', re.MULTILINE), self.header_key_format),
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)