from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QScrollArea
from typing import Callable

from ..icons import get_icon


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

        self.npm_install_btn = self._btn("npm install", self.npm_install, icon="system-run")
        self.npm_dev_btn = self._btn("npm run dev", self.npm_run_dev, icon="system-run")
        self.npm_build_btn = self._btn("npm run build", self.npm_run_build, icon="system-run")

        layout.addWidget(self.npm_install_btn)
        layout.addWidget(self.npm_dev_btn)
        layout.addWidget(self.npm_build_btn)

        layout.addStretch(1)

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

    def npm_run_dev(self) -> None:
        self.main_window.run_command(["npm", "run", "dev"])

    def npm_run_build(self) -> None:
        self.main_window.run_command(["npm", "run", "build"])
