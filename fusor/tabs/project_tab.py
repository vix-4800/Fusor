import os
import sys
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QScrollArea,
)
from ..ui import create_button, CONTENT_MARGIN


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
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)

        server_group = QGroupBox("Server Control")
        server_layout = QHBoxLayout()

        self.start_btn = create_button("Start", "media-playback-start")
        self.start_btn.clicked.connect(main_window.start_project)
        self.stop_btn = create_button(
            "Stop",
            "media-playback-stop",
            color="#dc3545",
        )
        self.stop_btn.clicked.connect(main_window.stop_project)
        server_layout.addWidget(self.start_btn)
        server_layout.addWidget(self.stop_btn)

        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        self.terminal_btn = create_button("Open Terminal", "utilities-terminal")
        self.terminal_btn.clicked.connect(self.open_terminal)
        layout.addWidget(self.terminal_btn)

        self.explorer_btn = create_button("Open Folder", "document-open")
        self.explorer_btn.clicked.connect(self.open_explorer)
        layout.addWidget(self.explorer_btn)

        # --- PHP Tools Group ---
        self.php_tools_group = QGroupBox("PHP Tools")
        php_layout = QVBoxLayout()

        self.phpunit_btn = create_button("Run PHPUnit", "system-run")
        self.phpunit_btn.clicked.connect(main_window.phpunit)
        self.rector_btn = create_button("Run Rector", "system-run")
        self.rector_btn.clicked.connect(
            lambda: main_window.run_command(
                [main_window.php_path, str(Path("vendor") / "bin" / "rector")]
            )
        )
        self.csfixer_btn = create_button("Run PHP CS-Fixer", "system-run")
        self.csfixer_btn.clicked.connect(
            lambda: main_window.run_command(
                [
                    main_window.php_path,
                    str(Path("vendor") / "bin" / "php-cs-fixer"),
                ]
            )
        )

        php_layout.addWidget(self.phpunit_btn)
        php_layout.addWidget(self.rector_btn)
        php_layout.addWidget(self.csfixer_btn)

        self.php_tools_group.setLayout(php_layout)
        layout.addWidget(self.php_tools_group)

        layout.addStretch(1)

        self.update_php_tools()

    def open_terminal(self) -> None:
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

    def open_explorer(self) -> None:
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
