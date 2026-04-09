from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from capture.mitm_capture import MitmCapture


class CaptureManager(QObject):
    session_captured = Signal(object)
    state_changed = Signal(str)
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.mitm = MitmCapture(self._on_mitm_session)
        self._running = False
        self._counter = 0  # 🔥 unique IDs

    def _on_mitm_session(self, data):
        from core.models import SessionRecord

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

            response_headers=data.get("response_headers", {}),
            response_body=data.get("response_body", ""),
        )

        self.session_captured.emit(session)
        print("DEBUG BODY:", session.response_body[:100])

    def start(self):
        import threading

        if self._running:
            return

        self._running = True

        t = threading.Thread(target=self.mitm.start, daemon=True)
        t.start()

        self.state_changed.emit("MITM Running")

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