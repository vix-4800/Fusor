from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
)
from pathlib import Path

import re

from ..ui import create_button, CONTENT_MARGIN, DEFAULT_SPACING
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
        self._layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        self._layout.setSpacing(DEFAULT_SPACING)

        self._buttons: list[QPushButton] = []
        self.update_commands()
        self._layout.addStretch(1)

    def update_commands(self) -> None:
        """Load make targets from the current project."""
        for btn in self._buttons:
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons = []

        path = Path(self.main_window.project_path) / "Makefile"
        targets = parse_makefile_targets(path)
        for name in targets:
            btn = create_button(name.replace("_", " ").capitalize(), "system-run")
            btn.clicked.connect(
                partial(self.main_window.run_command, ["make", name])
            )
            self._layout.addWidget(btn)
            self._buttons.append(btn)
        self.setVisible(bool(targets))
