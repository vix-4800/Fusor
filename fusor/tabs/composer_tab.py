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


class ComposerTab(QWidget):
    """Helpers for composer based workflows."""

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

        self.install_btn = self._btn(
            "Composer install", self.composer_install, icon="package-install"
        )
        self.update_btn = self._btn(
            "Composer update", self.composer_update, icon="system-software-update"
        )
        layout.addWidget(self.install_btn)
        layout.addWidget(self.update_btn)

        self.scripts_group = QGroupBox("Composer Scripts")
        self.scripts_layout = QVBoxLayout()
        self.scripts_group.setLayout(self.scripts_layout)
        layout.addWidget(self.scripts_group)

        layout.addStretch(1)

        self.update_composer_scripts()

    def _btn(self, text: str, slot: Callable[[], None], icon: str | None = None) -> QPushButton:
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def composer_install(self) -> None:
        self.main_window.run_command(["composer", "install"])

    def composer_update(self) -> None:
        self.main_window.run_command(["composer", "update"])

    def update_composer_scripts(self) -> None:
        scripts: list[str] = []
        path = self.main_window.project_path
        if path:
            composer = Path(path) / "composer.json"
            try:
                with open(composer, "r", encoding="utf-8") as f:
                    data = json.load(f)
                scr = data.get("scripts", {})
                if isinstance(scr, dict):
                    scripts = list(scr.keys())
            except OSError:
                pass

        for btn in getattr(self, "_script_buttons", []):
            self.scripts_layout.removeWidget(btn)
            btn.deleteLater()
        self._script_buttons = []

        for name in scripts:
            btn = self._btn(
                name.capitalize().replace('-', ' '),
                lambda _=False, n=name: self.main_window.run_command([
                    "composer",
                    "run",
                    n,
                ]),
                icon="system-run",
            )
            self.scripts_layout.addWidget(btn)
            self._script_buttons.append(btn)

        self.scripts_group.setVisible(bool(scripts))

