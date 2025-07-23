from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QScrollArea,
)
from pathlib import Path
from typing import Callable
import re

from ..icons import get_icon
from functools import partial


def parse_makefile_targets(path: Path) -> list[str]:
    """Return a list of targets defined in the Makefile at ``path``."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []

    targets: list[str] = []
    pattern = re.compile(r"^([A-Za-z0-9][^:#=\s]*)\s*:")
    for line in lines:
        m = pattern.match(line)
        if m:
            target = m.group(1)
            if target != ".PHONY" and target not in targets:
                targets.append(target)
    return targets


class MakefileTab(QWidget):
    """Display make targets as buttons."""

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

        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(12)

        self._buttons: list[QPushButton] = []
        self.update_commands()
        self._layout.addStretch(1)

    def _btn(self, text: str, slot: Callable[[], None], icon: str | None = None) -> QPushButton:
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def update_commands(self) -> None:
        """Load make targets from the current project."""
        for btn in self._buttons:
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons = []

        path = Path(self.main_window.project_path) / "Makefile"
        targets = parse_makefile_targets(path)
        for name in targets:
            btn = self._btn(
                name.replace("_", " ").capitalize(),
                partial(self.main_window.run_command, ["make", name]),
                icon="system-run",
            )
            self._layout.addWidget(btn)
            self._buttons.append(btn)
        self.setVisible(bool(targets))
