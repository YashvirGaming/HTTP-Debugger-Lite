from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    request_selected = Signal(int)
    start_capture = Signal()
    pause_capture = Signal()
    clear_requests = Signal()
    export_requests = Signal()
