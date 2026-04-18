from __future__ import annotations

from utils.mitm_manager import setup_mitm
from utils.proxy_manager import enable_proxy, disable_proxy
import atexit

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QSplitter, QVBoxLayout, QWidget

import json
import xml.etree.ElementTree as ET

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

        atexit.register(disable_proxy)

        self._build_ui()
        self._connect_signals()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self._do_refresh_table)
        
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
        self.signals.start_capture.connect(self._start_all)
        self.signals.pause_capture.connect(self._pause_all)

        self.signals.clear_requests.connect(self._on_clear_requests)

        self.signals.export_requests.connect(self._export_requests)

        self.capture_manager.session_captured.connect(self._on_session_captured)
        self.capture_manager.state_changed.connect(self.status_bar_widget.set_state)
        self.capture_manager.error.connect(self._on_error)

        self.store.changed.connect(self.refresh_table)

        self.filter_bar.search_input.textChanged.connect(self.refresh_table)
        self.filter_bar.search_input.returnPressed.connect(self.refresh_table)
        
        self.filter_bar.method_combo.currentTextChanged.connect(self.refresh_table)
        self.filter_bar.status_combo.currentTextChanged.connect(self.refresh_table)
        self.filter_bar.type_combo.currentTextChanged.connect(self.refresh_table)

    def _start_all(self):
        try:
            if not self.mitm_process:
                self.mitm_process = setup_mitm()

            enable_proxy("127.0.0.1", 8080)
            self.capture_manager.start()

        except Exception as e:
            disable_proxy()
            print("START ERROR:", e)

    def _pause_all(self):
        disable_proxy()

        if self.mitm_process:
            self.mitm_process.terminate()
            self.mitm_process = None

        self.capture_manager.pause()
        self.status_bar_widget.set_state("Paused (Proxy OFF)")

    def _on_session_captured(self, session) -> None:
        self.store.upsert(session)
        self.status_bar_widget.increment_requests()

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

    def _on_clear_requests(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear Requests",
            "Clear all captured requests?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.store.clear()
        self.current_session_id = None

        self.request_tabs.update_data(None)
        self.response_tabs.update_data(None)

        self.status_bar_widget.set_selected("None")
        self.status_bar_widget.set_info("Cleared (Capture still running)")

    def _export_requests(self):
        sessions = self.store.all()

        if not sessions:
            self.status_bar_widget.set_info("No data to export")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Requests",
            "requests.json",
            "JSON Files (*.json);;XML Files (*.xml);;Text Files (*.txt)"
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".json"):
                self._export_json(file_path, sessions)

            elif file_path.endswith(".xml"):
                self._export_xml(file_path, sessions)

            else:
                self._export_txt(file_path, sessions)

            self.status_bar_widget.set_info(f"Exported → {file_path}")

        except Exception as e:
            self.status_bar_widget.set_info(f"Export failed: {e}")

    def _export_json(self, path, sessions):
        data = []

        for s in sessions:
            data.append({
                "id": s.id,
                "method": s.method,
                "url": s.url,
                "status": s.status,
                "headers": s.request_headers,
                "body": s.request_body,
                "response_headers": s.response_headers,
                "response_body": s.response_body,
                "type": s.type,
                "size": s.size,
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _export_xml(self, path, sessions):
        root = ET.Element("requests")

        for s in sessions:
            req = ET.SubElement(root, "request")

            ET.SubElement(req, "id").text = str(s.id)
            ET.SubElement(req, "method").text = s.method
            ET.SubElement(req, "url").text = s.url or ""
            ET.SubElement(req, "status").text = str(s.status)

            headers = ET.SubElement(req, "headers")
            for k, v in (s.request_headers or {}).items():
                h = ET.SubElement(headers, "header")
                h.set("name", k)
                h.text = v

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _export_txt(self, path, sessions):
        with open(path, "w", encoding="utf-8") as f:
            for s in sessions:
                f.write(f"{s.method} {s.url}\n")
                f.write(f"Status: {s.status}\n")
                f.write("-" * 50 + "\n")

    def refresh_table(self) -> None:
        self.refresh_timer.start(100)

    def _do_refresh_table(self) -> None:
        import traceback

        try:
            sessions = self.store.filtered(
                self.filter_bar.search_input.text(),
                self.filter_bar.method_combo.currentText(),
                self.filter_bar.status_combo.currentText(),
                self.filter_bar.type_combo.currentText(),
            )

            print("sessions:", len(sessions))

            self.request_table.load_sessions(sessions)
            print("table loaded")

            self.status_bar_widget.update_status_counts(sessions)
            print("status updated")

            last_time = 0
            if sessions:
                last = sessions[-1]
                if hasattr(last, "duration_ms"):
                    last_time = last.duration_ms or 0

            self.status_bar_widget.set_last_time(last_time)

            self.status_bar_widget.set_total(len(self.store.all()))
            self.status_bar_widget.set_filtered(len(sessions))

            print("refresh done")

        except Exception:
            traceback.print_exc()

    # 🔥 VERY IMPORTANT: ALWAYS DISABLE PROXY ON EXIT
    def closeEvent(self, event):
        disable_proxy()

        if self.mitm_process:
            self.mitm_process.terminate()

        self.capture_manager.stop()
        super().closeEvent(event)