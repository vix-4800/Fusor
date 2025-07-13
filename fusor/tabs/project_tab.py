from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)

class ProjectTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        start_btn = self._btn("▶ Start", main_window.start_project)
        stop_btn = self._btn("■ Stop", main_window.stop_project)
        row1 = QHBoxLayout()
        row1.addWidget(start_btn)
        row1.addWidget(stop_btn)
        layout.addLayout(row1)

        layout.addWidget(self._btn("Run PHPUnit", main_window.phpunit))
        
        self.composer_install_btn = self._btn(
            "Composer install",
            lambda: main_window.run_command(["composer", "install"]),
        )
        layout.addWidget(self.composer_install_btn)

        self.composer_update_btn = self._btn(
            "Composer update",
            lambda: main_window.run_command(["composer", "update"]),
        )
        layout.addWidget(self.composer_update_btn)

        layout.addStretch(1)

    def _btn(self, label, slot):
        btn = QPushButton(label)
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn
