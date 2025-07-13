from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QCheckBox, QSizePolicy, QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import QTimer, Qt

class LogsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(16)

        # --- Log Output ---
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("No logs loaded yet...")
        self.log_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        outer_layout.addWidget(self.log_view)

        # --- Controls Group ---
        control_box = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.clicked.connect(self.main_window.refresh_logs)
        refresh_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        control_layout.addWidget(refresh_btn)

        self.auto_checkbox = QCheckBox("Auto refresh (5s)")
        self.auto_checkbox.setMinimumHeight(36)
        self.auto_checkbox.setChecked(False)
        control_layout.addWidget(self.auto_checkbox, alignment=Qt.AlignmentFlag.AlignVCenter)

        control_box.setLayout(control_layout)
        outer_layout.addWidget(control_box)

        outer_layout.addStretch(1)

        # Expose log view to main_window
        self.main_window.log_view = self.log_view

        # Timer for auto-refresh
        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self.main_window.refresh_logs)
        self.auto_checkbox.toggled.connect(self.on_auto_refresh_toggled)

    def on_auto_refresh_toggled(self, checked: bool):
        if checked:
            self._timer.start()
            self.main_window.refresh_logs()
        else:
            self._timer.stop()
