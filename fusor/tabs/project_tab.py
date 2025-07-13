from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class ProjectTab(QWidget):
    """Tab with common project actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        start_btn = QPushButton("Start")
        start_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        start_btn.clicked.connect(self.main_window.start_project)
        layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stop_btn.clicked.connect(self.main_window.stop_project)
        layout.addWidget(stop_btn)
