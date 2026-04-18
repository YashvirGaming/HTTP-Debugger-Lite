from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer
import time


class StatusBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBarFrame")
        self.setMinimumHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)

        self.state_label = QLabel("State: Idle")
        self.proxy_label = QLabel("Proxy: OFF")
        self.rps_label = QLabel("RPS: 0/s")
        self.total_label = QLabel("Total: 0")
        self.filtered_label = QLabel("Visible: 0")
        self.status_counts_label = QLabel("200:0 403:0 500:0")
        self.last_time_label = QLabel("Last: - ms")
        self.info_label = QLabel("Ready")
        self.selected_label = QLabel("Selected: None")

        layout.addWidget(self.state_label)
        layout.addWidget(self.proxy_label)
        layout.addWidget(self.rps_label)
        layout.addWidget(self.total_label)
        layout.addWidget(self.filtered_label)
        layout.addWidget(self.status_counts_label)
        layout.addWidget(self.last_time_label)
        layout.addWidget(self.info_label)
        layout.addStretch()
        layout.addWidget(self.selected_label)

        self.req_counter = 0
        self.last_tick = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_rps)
        self.timer.start(1000)

    def _update_rps(self):
        now = time.time()
        elapsed = now - self.last_tick
        rps = int(self.req_counter / elapsed) if elapsed > 0 else 0
        self.rps_label.setText(f"RPS: {rps}/s")
        self.req_counter = 0
        self.last_tick = now

    def increment_requests(self):
        self.req_counter += 1

    def set_state(self, text: str) -> None:
        self.state_label.setText(f"State: {text}")

        if "Running" in text:
            self.state_label.setStyleSheet("color:#22c55e;")
            self.proxy_label.setText("Proxy: ON")
            self.proxy_label.setStyleSheet("color:#22c55e;")
        else:
            self.state_label.setStyleSheet("color:#ef4444;")
            self.proxy_label.setText("Proxy: OFF")
            self.proxy_label.setStyleSheet("color:#ef4444;")

    def set_total(self, value: int) -> None:
        self.total_label.setText(f"Total: {value}")

    def set_filtered(self, value: int) -> None:
        self.filtered_label.setText(f"Visible: {value}")

    def set_selected(self, text: str) -> None:
        self.selected_label.setText(f"Selected: {text}")

    def set_info(self, text: str) -> None:
        self.info_label.setText(text)

    def update_status_counts(self, sessions):
        s200 = sum(1 for s in sessions if s.status == 200)
        s403 = sum(1 for s in sessions if s.status == 403)
        s500 = sum(1 for s in sessions if s.status == 500)

        self.status_counts_label.setText(f"200:{s200} 403:{s403} 500:{s500}")

    def set_last_time(self, ms):
        self.last_time_label.setText(f"Last: {ms} ms")