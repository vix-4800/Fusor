from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QSizePolicy

class LogsTab(QWidget):
    """Tab that displays log text and allows refreshing."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.log_view)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        refresh_btn.clicked.connect(self.main_window.refresh_logs)
        layout.addWidget(refresh_btn)

        # expose log view so main window can update it
        self.main_window.log_view = self.log_view
