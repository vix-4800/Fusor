import os
import sys
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
    QScrollArea,
)
from ..icons import get_icon


class ProjectTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        server_group = QGroupBox("Server Control")
        server_layout = QHBoxLayout()

        self.start_btn = self._btn(
            "Start",
            main_window.start_project,
            icon="media-playback-start",
        )
        self.stop_btn = self._btn(
            "Stop",
            main_window.stop_project,
            icon="media-playback-stop",
        )
        server_layout.addWidget(self.start_btn)
        server_layout.addWidget(self.stop_btn)

        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        # --- PHP Tools Group ---
        self.php_tools_group = QGroupBox("PHP Tools")
        php_layout = QVBoxLayout()

        self.phpunit_btn = self._btn(
            "Run PHPUnit",
            main_window.phpunit,
            icon="system-run",
        )
        self.rector_btn = self._btn(
            "Run Rector",
            lambda: main_window.run_command([main_window.php_path, str(Path("vendor") / "bin" / "rector")]),
            icon="system-run",
        )
        self.csfixer_btn = self._btn(
            "Run PHP CS-Fixer",
            lambda: main_window.run_command([main_window.php_path, str(Path("vendor") / "bin" / "php-cs-fixer")]),
            icon="system-run",
        )

        php_layout.addWidget(self.phpunit_btn)
        php_layout.addWidget(self.rector_btn)
        php_layout.addWidget(self.csfixer_btn)

        self.php_tools_group.setLayout(php_layout)
        layout.addWidget(self.php_tools_group)

        self.terminal_btn = self._btn(
            "Open Terminal",
            self.open_terminal,
            icon="utilities-terminal",
        )
        layout.addWidget(self.terminal_btn)

        self.explorer_btn = self._btn(
            "Open Folder",
            self.open_explorer,
            icon="document-open",
        )
        layout.addWidget(self.explorer_btn)

        composer_group = QGroupBox("Composer")
        composer_layout = QVBoxLayout()
        self.composer_install_btn = self._btn(
            "Composer install",
            lambda: main_window.run_command(["composer", "install"]),
            icon="package-install",
        )
        self.composer_update_btn = self._btn(
            "Composer update",
            lambda: main_window.run_command(["composer", "update"]),
            icon="system-software-update",
        )
        composer_layout.addWidget(self.composer_install_btn)
        composer_layout.addWidget(self.composer_update_btn)
        composer_group.setLayout(composer_layout)
        layout.addWidget(composer_group)

        layout.addStretch(1)

        self.update_php_tools()

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

        if sys.platform == "darwin":
            cmd = ["open", "-a", "Terminal", path]
            cwd = None
        else:
            cmd = ["cmd.exe"] if os.name == "nt" else ["x-terminal-emulator"]
            cwd = path

        try:
            subprocess.Popen(cmd, cwd=cwd)
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")

    def open_explorer(self):
        """Open the project directory in the system file explorer."""
        path = self.main_window.project_path
        if not path:
            print("Project path not set")
            return

        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
            return

        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
            return

        try:
            subprocess.Popen(["xdg-open", path])
        except FileNotFoundError:
            subprocess.Popen(["gio", "open", path])

    def update_php_tools(self) -> None:
        """Enable or disable PHP tool buttons based on composer.json."""
        packages: set[str] = set()
        path = self.main_window.project_path
        if path:
            composer = Path(path) / "composer.json"
            try:
                with open(composer, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key in ("require", "require-dev"):
                    pkgs = data.get(key, {})
                    if isinstance(pkgs, dict):
                        packages.update(pkgs.keys())
            except OSError:
                pass

        mapping = {
            "phpunit/phpunit": self.phpunit_btn,
            "rector/rector": self.rector_btn,
            "friendsofphp/php-cs-fixer": self.csfixer_btn,
        }
        for pkg, btn in mapping.items():
            btn.setEnabled(pkg in packages)
