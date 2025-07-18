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


class YiiTab(QWidget):
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

        self.console_group = QGroupBox("Yii Console")
        console_layout = QVBoxLayout()
        console_layout.setSpacing(10)

        self.cache_flush_btn = self._btn(
            "Cache Flush",
            lambda: self.main_window.yii("cache/flush-all"),
            icon="view-refresh",
        )
        self.migrate_btn = self._btn(
            "Migrate",
            lambda: self.main_window.yii("migrate"),
            icon="system-run",
        )
        self.make_migration_btn = self._btn(
            "Make Migration",
            lambda: self.main_window.yii("migrate/create"),
            icon="document-new",
        )

        console_layout.addWidget(self.cache_flush_btn)
        console_layout.addWidget(self.migrate_btn)
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
        visible = text == "Yii"
        self.console_group.setVisible(visible)
