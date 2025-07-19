from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
    QScrollArea,
)

from ..icons import get_icon
from typing import Callable


class SymfonyTab(QWidget):
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
        layout.setSpacing(20)

        self.console_group = QGroupBox("Symfony Console")
        console_layout = QVBoxLayout()
        console_layout.setSpacing(10)

        self.cache_clear_btn = self._btn(
            "Cache Clear",
            lambda: self.main_window.symfony("cache:clear"),
            icon="view-refresh",
        )
        self.migrate_btn = self._btn(
            "Migrate",
            lambda: self.main_window.symfony("doctrine:migrations:migrate"),
            icon="system-run",
        )
        self.status_btn = self._btn(
            "Migration Status",
            lambda: self.main_window.symfony("doctrine:migrations:status"),
            icon="dialog-information",
        )
        self.make_migration_btn = self._btn(
            "Make Migration",
            lambda: self.main_window.symfony("make:migration"),
            icon="document-new",
        )

        console_layout.addWidget(self.cache_clear_btn)
        console_layout.addWidget(self.migrate_btn)
        console_layout.addWidget(self.status_btn)
        console_layout.addWidget(self.make_migration_btn)
        self.console_group.setLayout(console_layout)
        layout.addWidget(self.console_group)

        layout.addStretch(1)

        self.on_framework_changed(self.main_window.framework_choice)

    def _btn(
        self, text: str, slot: Callable[[], None], icon: str | None = None
    ) -> QPushButton:
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def on_framework_changed(self, text: str) -> None:
        visible = text == "Symfony"
        self.console_group.setVisible(visible)
