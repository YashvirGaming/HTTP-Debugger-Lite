from __future__ import annotations
from PySide6.QtCore import QObject, Signal
from capture.mitm_capture import MitmCapture


class CaptureManager(QObject):
    session_captured = Signal(object)
    state_changed = Signal(str)
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.mitm = MitmCapture(self._safe_callback)
        self._running = False
        self._counter = 0  # 🔥 unique IDs

    def _safe_callback(self, data):
        try:
            self._on_mitm_session(data)
        except Exception as e:
            self.error.emit(str(e))

    def _on_mitm_session(self, data):
        from core.models import SessionRecord

        try:
            self._counter += 1

            session = SessionRecord(
                id=self._counter,
                method=data.get("method", ""),
                url=data.get("url", ""),
                host=data.get("host", ""),
                status=data.get("status", 0),
                type=data.get("type", ""),
                size=data.get("size", 0),
                request_headers=data.get("headers", {}),
                request_body=data.get("body", ""),
                request_bytes=data.get("request_bytes", b""),
                response_headers=data.get("response_headers", {}),
                response_body=data.get("response_body", ""),
                response_bytes=data.get("response_bytes", b""),
            )

            self.session_captured.emit(session)

        except Exception as e:
            self.error.emit(str(e))

    def start(self):
        if self._running:
            return

        self._running = True

        self.mitm.start()

        self.state_changed.emit("Running (MITM + Proxy)")

    def pause(self) -> None:
        if not self._running:
            return

        self.stop()

    def stop(self):
        if not self._running:
            return

        self.mitm.stop()
        self._running = False

        self.state_changed.emit("Stopped")