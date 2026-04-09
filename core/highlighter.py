from PySide6.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter
import re


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # 🔥 COLORS (neon style)
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#60a5fa"))  # blue

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#22c55e"))  # green

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#f59e0b"))  # yellow

        self.bool_format = QTextCharFormat()
        self.bool_format.setForeground(QColor("#ef4444"))  # red

        # 🔥 REGEX RULES
        self.rules = [
            (re.compile(r'"[^"]*"\s*:'), self.key_format),   # keys
            (re.compile(r':\s*"[^"]*"'), self.string_format),  # string values
            (re.compile(r'\b\d+\b'), self.number_format),  # numbers
            (re.compile(r'\b(true|false|null)\b'), self.bool_format),  # bool/null
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, fmt)