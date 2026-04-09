from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel


class StatusBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBarFrame")
        self.setMinimumHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(18)

        self.state_label = QLabel("State: Idle")
        self.total_label = QLabel("Total Requests: 0")
        self.filtered_label = QLabel("Visible: 0")
        self.selected_label = QLabel("Selected: None")
        self.info_label = QLabel("Needs admin rights for live capture")

        layout.addWidget(self.state_label)
        layout.addWidget(self.total_label)
        layout.addWidget(self.filtered_label)
        layout.addWidget(self.info_label)
        layout.addStretch()
        layout.addWidget(self.selected_label)

    def set_state(self, text: str) -> None:
        self.state_label.setText(f"State: {text}")

    def set_total(self, value: int) -> None:
        self.total_label.setText(f"Total Requests: {value}")

    def set_filtered(self, value: int) -> None:
        self.filtered_label.setText(f"Visible: {value}")

    def set_selected(self, text: str) -> None:
        self.selected_label.setText(f"Selected: {text}")

    def set_info(self, text: str) -> None:
        self.info_label.setText(text)
