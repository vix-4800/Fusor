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
from ..icons import get_icon

class ProjectTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        server_group = QGroupBox("Server Control")
        server_layout = QHBoxLayout()
        start_btn = self._btn(
            "▶ Start",
            main_window.start_project,
            icon="media-playback-start",
        )
        stop_btn = self._btn(
            "■ Stop",
            main_window.stop_project,
            icon="media-playback-stop",
        )
        server_layout.addWidget(start_btn)
        server_layout.addWidget(stop_btn)
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        phpunit_btn = self._btn(
            "🧪 Run PHPUnit",
            main_window.phpunit,
            icon="system-run",
        )
        layout.addWidget(phpunit_btn)

        self.terminal_btn = self._btn(
            "Open Terminal",
            self.open_terminal,
            icon="utilities-terminal",
        )
        layout.addWidget(self.terminal_btn)

        composer_group = QGroupBox("Composer")
        composer_layout = QVBoxLayout()
        self.composer_install_btn = self._btn(
            "📦 Composer install",
            lambda: main_window.run_command(["composer", "install"]),
            icon="package-install",
        )
        self.composer_update_btn = self._btn(
            "⬆ Composer update",
            lambda: main_window.run_command(["composer", "update"]),
            icon="system-software-update",
        )
        composer_layout.addWidget(self.composer_install_btn)
        composer_layout.addWidget(self.composer_update_btn)
        composer_group.setLayout(composer_layout)
        layout.addWidget(composer_group)

        layout.addStretch(1)

    def _btn(self, label, slot, icon: str | None = None):
        btn = QPushButton(label)
        if icon:
            btn.setIcon(get_icon(icon))
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
