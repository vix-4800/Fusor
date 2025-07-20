from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QGroupBox,
)
from typing import Callable
from pathlib import Path
import json

from ..icons import get_icon
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.npm_install_btn = self._btn(
            "npm install", self.npm_install, icon="system-run"
        )

        layout.addWidget(self.npm_install_btn)

        self.npm_scripts_group = QGroupBox("NPM Scripts")
        self.npm_scripts_layout = QVBoxLayout()
        self.npm_scripts_group.setLayout(self.npm_scripts_layout)
        layout.addWidget(self.npm_scripts_group)

        layout.addStretch(1)

        self.update_npm_scripts()

    def _btn(self, text: str, slot: Callable[[], None], icon: str | None = None) -> QPushButton:
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

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
            btn = self._btn(
                name.capitalize().replace('-', ' '),
                partial(self.main_window.run_command, ["npm", "run", name]),
                icon="system-run",
            )
            self.npm_scripts_layout.addWidget(btn)
            self._script_buttons.append(btn)

        self.npm_scripts_group.setVisible(bool(scripts))
