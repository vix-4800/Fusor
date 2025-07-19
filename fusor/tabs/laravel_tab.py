from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
    QScrollArea,
)

from ..icons import get_icon


class LaravelTab(QWidget):
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

        # --- Laravel Migrations ---
        self.migrate_group = QGroupBox("Laravel Migrations")
        migrate_layout = QVBoxLayout()
        migrate_layout.setSpacing(10)
        migrate_layout.addWidget(
            self._btn("Migrate", self.main_window.migrate, icon="system-run")
        )
        migrate_layout.addWidget(
            self._btn("Rollback", self.main_window.rollback, icon="edit-undo")
        )
        migrate_layout.addWidget(
            self._btn("Fresh", self.main_window.fresh, icon="view-refresh")
        )
        migrate_layout.addWidget(
            self._btn("Seed", self.main_window.seed, icon="list-add")
        )
        self.migrate_group.setLayout(migrate_layout)
        layout.addWidget(self.migrate_group)

        # --- Laravel Artisan Commands ---
        self.artisan_group = QGroupBox("Laravel Artisan")
        artisan_layout = QVBoxLayout()
        artisan_layout.setSpacing(10)
        self.optimize_btn = self._btn(
            "Optimize",
            lambda: self.main_window.artisan("optimize"),
            icon="preferences-system",
        )
        self.config_clear_btn = self._btn(
            "Config Clear",
            lambda: self.main_window.artisan("config:clear"),
            icon="edit-clear",
        )
        artisan_layout.addWidget(self.optimize_btn)
        artisan_layout.addWidget(self.config_clear_btn)
        self.artisan_group.setLayout(artisan_layout)
        layout.addWidget(self.artisan_group)

        layout.addStretch(1)

        self.on_framework_changed(self.main_window.framework_choice)

    def _btn(self, text, slot, icon: str | None = None):
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def on_framework_changed(self, text: str):
        visible = text == "Laravel"
        self.migrate_group.setVisible(visible)
        self.artisan_group.setVisible(visible)
