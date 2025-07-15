import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
)

class ProjectTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        server_group = QGroupBox("Server Control")
        server_layout = QHBoxLayout()
        self.start_btn = self._btn("▶ Start", main_window.start_project)
        self.stop_btn = self._btn("■ Stop", main_window.stop_project)
        server_layout.addWidget(self.start_btn)
        server_layout.addWidget(self.stop_btn)
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        phpunit_btn = self._btn("🧪 Run PHPUnit", main_window.phpunit)
        layout.addWidget(phpunit_btn)

        self.terminal_btn = self._btn("Open Terminal", self.open_terminal)
        layout.addWidget(self.terminal_btn)

        composer_group = QGroupBox("Composer")
        composer_layout = QVBoxLayout()
        self.composer_install_btn = self._btn(
            "📦 Composer install",
            lambda: main_window.run_command(["composer", "install"])
        )
        self.composer_update_btn = self._btn(
            "⬆ Composer update",
            lambda: main_window.run_command(["composer", "update"])
        )
        composer_layout.addWidget(self.composer_install_btn)
        composer_layout.addWidget(self.composer_update_btn)
        composer_group.setLayout(composer_layout)
        layout.addWidget(composer_group)

        layout.addStretch(1)

    def _btn(self, label, slot):
        btn = QPushButton(label)
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def open_terminal(self):
        """Open a new terminal window in the current project directory."""
        path = self.main_window.project_path
        if not path:
            print("Project path not set")
            return

        cmd = ["cmd.exe"] if os.name == "nt" else ["x-terminal-emulator"]
        try:
            subprocess.Popen(cmd, cwd=path)
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
