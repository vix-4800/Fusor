from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGroupBox,
)
from pathlib import Path
import json

from ..ui import create_button, CONTENT_MARGIN, DEFAULT_SPACING
from functools import partial


class NodeTab(QWidget):
    """Simple helpers for npm-based workflows."""

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
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(DEFAULT_SPACING)

        self.npm_install_btn = create_button("npm install", "system-run")
        self.npm_install_btn.clicked.connect(self.npm_install)

        layout.addWidget(self.npm_install_btn)

        self.npm_scripts_group = QGroupBox("NPM Scripts")
        self.npm_scripts_layout = QVBoxLayout()
        self.npm_scripts_group.setLayout(self.npm_scripts_layout)
        layout.addWidget(self.npm_scripts_group)

        layout.addStretch(1)

        self.update_npm_scripts()

    def npm_install(self) -> None:
        self.main_window.run_command(["npm", "install"])

    def update_npm_scripts(self) -> None:
        """Load npm scripts from package.json and create buttons."""
        scripts: list[str] = []
        path = self.main_window.project_path
        if path:
            package = Path(path) / "package.json"
            try:
                with open(package, "r", encoding="utf-8") as f:
                    data = json.load(f)
                scr = data.get("scripts", {})
                if isinstance(scr, dict):
                    scripts = list(scr.keys())
            except OSError:
                pass

        for btn in getattr(self, "_script_buttons", []):
            self.npm_scripts_layout.removeWidget(btn)
            btn.deleteLater()
        self._script_buttons = []

        for name in scripts:
            btn = create_button(
                name.capitalize().replace("-", " "), "system-run"
            )
            btn.clicked.connect(
                partial(self.main_window.run_command, ["npm", "run", name])
            )
            self.npm_scripts_layout.addWidget(btn)
            self._script_buttons.append(btn)

        self.npm_scripts_group.setVisible(bool(scripts))
