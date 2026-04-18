APP_TITLE = "HTTP Debugger Lite"
APP_WIDTH = 1550
APP_HEIGHT = 930

METHODS = ["ALL", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TLS"]
STATUS_GROUPS = ["ALL", "2xx", "3xx", "4xx", "5xx"]
CONTENT_TYPES = ["ALL", "json", "html", "js", "css", "image", "text", "tls", "other"]

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0b1020;
    color: #e5ecff;
    font-family: Orbitron, Segoe UI;
    font-size: 10pt;
}

QFrame#TopBar,
QFrame#StatusBarFrame,
QFrame#PaneFrame {
    background-color: #121a2f;
    border: 1px solid #22304f;
    border-radius: 12px;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QTabWidget::pane {
    background-color: #0f1730;
    border: 1px solid #2d3d66;
    border-radius: 10px;
    color: #e5ecff;
    padding: 6px;
}

QComboBox QAbstractItemView {
    background-color: #0f1730;
    color: #e5ecff;
    selection-background-color: #1d4ed8;
    border: 1px solid #2d3d66;
}

QPushButton {
    background-color: #182443;
    border: 1px solid #31456f;
    border-radius: 10px;
    padding: 8px 14px;
    color: #f3f7ff;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #203056;
}

QPushButton:pressed {
    background-color: #14203b;
}

QHeaderView::section {
    background-color: #16213f;
    color: #dbe7ff;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2a3a63;
    font-weight: 700;
}

QTableWidget {
    background-color: #0f1730;
    alternate-background-color: #111c39;
    gridline-color: #233252;
    border: 1px solid #22304f;
    border-radius: 12px;
    selection-background-color: #1d4ed8;
    selection-color: #ffffff;
}

QTabBar::tab {
    background: #16213f;
    color: #cfe0ff;
    padding: 8px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background: #1d4ed8;
    color: white;
}

QLabel#TitleLabel {
    font-size: 20pt;
    font-weight: 900;
    color: #60a5fa;
}

QLabel#SubTitleLabel {
    font-size: 10pt;
    color: #8ea7d8;
}

QLabel#SectionTitle {
    font-size: 11pt;
    font-weight: 700;
    color: #d9e7ff;
}

QSplitter::handle {
    background-color: #22304f;
}

QStatusBar {
    background-color: #121a2f;
    color: #d8e4ff;
}
"""