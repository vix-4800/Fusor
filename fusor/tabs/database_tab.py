from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy


class DatabaseTab(QWidget):
    """Tab with quick database helpers."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        dbeaver_btn = QPushButton("Open in DBeaver")
        dbeaver_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dbeaver_btn.clicked.connect(lambda: print("Open in DBeaver clicked"))
        layout.addWidget(dbeaver_btn)

        dump_btn = QPushButton("Dump to SQL")
        dump_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dump_btn.clicked.connect(lambda: print("Dump to SQL clicked"))
        layout.addWidget(dump_btn)

        restore_btn = QPushButton("Restore dump")
        restore_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        restore_btn.clicked.connect(lambda: print("Restore dump clicked"))
        layout.addWidget(restore_btn)
