from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy

from utils.constants import CONTENT_TYPES, METHODS, STATUS_GROUPS


class FilterBar(QFrame):
    def __init__(self, signals, parent=None):
        super().__init__(parent)
        self.signals = signals
        self.setObjectName("TopBar")
        self.setMinimumHeight(86)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        self.title_label = QLabel("HTTP Debugger Lite")
        self.title_label.setObjectName("TitleLabel")
        self.subtitle_label = QLabel("Built By Yashvir Gaming")
        self.subtitle_label.setObjectName("SubTitleLabel")

        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Stop/Pause")
        self.clear_btn = QPushButton("Clear")

        # 🔥 ADD THIS HERE
        self.export_btn = QPushButton("Export")
        self.export_btn.setCursor(Qt.PointingHandCursor)

        self.method_combo = QComboBox()
        self.method_combo.addItems(METHODS)
        self.status_combo = QComboBox()
        self.status_combo.addItems(STATUS_GROUPS)
        self.type_combo = QComboBox()
        self.type_combo.addItems(CONTENT_TYPES)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search URL, host, method...")

        for btn in (self.start_btn, self.pause_btn, self.clear_btn):
            btn.setCursor(Qt.PointingHandCursor)

        self.start_btn.clicked.connect(self.signals.start_capture.emit)
        self.pause_btn.clicked.connect(self.signals.pause_capture.emit)
        self.clear_btn.clicked.connect(self.signals.clear_requests.emit)
        self.export_btn.clicked.connect(self.signals.export_requests.emit)

        title_wrap = QFrame()
        title_wrap.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 14, 0)
        title_layout.setSpacing(8)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        layout.addWidget(title_wrap)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.clear_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(QLabel("Method"))
        layout.addWidget(self.method_combo)
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self.status_combo)
        layout.addWidget(QLabel("Type"))
        layout.addWidget(self.type_combo)
        layout.addWidget(self.search_input, 1)

        self.method_combo.setMinimumWidth(100)
        self.status_combo.setMinimumWidth(90)
        self.type_combo.setMinimumWidth(100)
        self.search_input.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
