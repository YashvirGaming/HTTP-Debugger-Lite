from __future__ import annotations

from utils.mitm_manager import setup_mitm
from utils.proxy_manager import enable_proxy, disable_proxy
import atexit

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget

from capture.capture_manager import CaptureManager
from core.session_store import SessionStore
from gui.filter_bar import FilterBar
from gui.request_table import RequestTable
from gui.request_tabs import RequestTabs
from gui.response_tabs import ResponseTabs
from gui.status_bar import StatusBarWidget
from utils.constants import APP_HEIGHT, APP_TITLE, APP_WIDTH, DARK_STYLESHEET
from utils.signals import AppSignals


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        self.mitm_process = None
        self.signals = AppSignals()
        self.store = SessionStore()
        self.capture_manager = CaptureManager()
        self.current_session_id: int | None = None

        self.setWindowTitle(APP_TITLE)
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(DARK_STYLESHEET)

        # 🔥 AUTO CLEANUP (VERY IMPORTANT)
        atexit.register(disable_proxy)

        self._build_ui()
        self._connect_signals()
        self.refresh_table()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.filter_bar = FilterBar(self.signals)
        self.request_table = RequestTable(self.signals)
        self.request_tabs = RequestTabs()
        self.response_tabs = ResponseTabs()
        self.status_bar_widget = StatusBarWidget()

        bottom_split = QSplitter(Qt.Horizontal)
        bottom_split.addWidget(self.request_tabs)
        bottom_split.addWidget(self.response_tabs)
        bottom_split.setSizes([700, 700])

        main_split = QSplitter(Qt.Vertical)
        main_split.addWidget(self.request_table)
        main_split.addWidget(bottom_split)
        main_split.setSizes([420, 380])

        root.addWidget(self.filter_bar)
        root.addWidget(main_split, 1)
        root.addWidget(self.status_bar_widget)

    def _connect_signals(self) -> None:
        self.signals.request_selected.connect(self._on_request_selected)

        # 🔥 REPLACED WITH PROXY-AWARE METHODS
        self.signals.start_capture.connect(self._start_all)
        self.signals.pause_capture.connect(self._pause_all)

        self.signals.clear_requests.connect(self._on_clear_requests)

        self.capture_manager.session_captured.connect(self._on_session_captured)
        self.capture_manager.state_changed.connect(self.status_bar_widget.set_state)
        self.capture_manager.error.connect(self._on_error)

        self.store.changed.connect(self.refresh_table)

        self.filter_bar.search_input.textChanged.connect(self.refresh_table)
        self.filter_bar.method_combo.currentTextChanged.connect(self.refresh_table)
        self.filter_bar.status_combo.currentTextChanged.connect(self.refresh_table)
        self.filter_bar.type_combo.currentTextChanged.connect(self.refresh_table)

    # 🔥 START (Proxy + Capture)
    def _start_all(self):
        if not self.mitm_process:
            self.mitm_process = setup_mitm()

        enable_proxy("127.0.0.1", 8080)

        self.capture_manager.start()
        self.status_bar_widget.set_state("Running (MITM + Proxy ON)")

    # 🔥 PAUSE (Proxy OFF)
    def _pause_all(self):
        disable_proxy()

        if self.mitm_process:
            self.mitm_process.terminate()
            self.mitm_process = None

        self.capture_manager.pause()
        self.status_bar_widget.set_state("Paused (Proxy OFF)")

    def _on_session_captured(self, session) -> None:
        self.store.upsert(session)

    def _on_error(self, message: str) -> None:
        self.status_bar_widget.set_info(message)
        QMessageBox.warning(self, "Capture Error", message)

    def _on_request_selected(self, session_id: int) -> None:
        self.current_session_id = session_id
        session = self.store.get_by_id(session_id)

        self.request_tabs.update_data(session)
        self.response_tabs.update_data(session)

        if session:
            self.status_bar_widget.set_selected(
                f"#{session.id} {session.method} {session.status or '-'}"
            )

    # 🔥 CLEAR = ALSO DISABLE PROXY
    def _on_clear_requests(self) -> None:
        disable_proxy()
        self.store.clear()
        self.current_session_id = None
        self.request_tabs.update_data(None)
        self.response_tabs.update_data(None)
        self.status_bar_widget.set_selected("None")
        self.status_bar_widget.set_info("Cleared")

    def refresh_table(self) -> None:
        sessions = self.store.filtered(
            self.filter_bar.search_input.text(),
            self.filter_bar.method_combo.currentText(),
            self.filter_bar.status_combo.currentText(),
            self.filter_bar.type_combo.currentText(),
        )

        self.request_table.load_sessions(sessions)
        self.status_bar_widget.set_total(len(self.store.all()))
        self.status_bar_widget.set_filtered(len(sessions))

    # 🔥 VERY IMPORTANT: ALWAYS DISABLE PROXY ON EXIT
    def closeEvent(self, event):
        disable_proxy()

        if self.mitm_process:
            self.mitm_process.terminate()

        self.capture_manager.stop()
        super().closeEvent(event)