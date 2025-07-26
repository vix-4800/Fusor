from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QScrollArea,
)

from ..ui import create_button, CONTENT_MARGIN


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
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(20)

        # --- Laravel Migrations ---
        self.migrate_group = QGroupBox("Laravel Migrations")
        migrate_layout = QVBoxLayout()
        migrate_layout.setSpacing(10)
        btn = create_button("Migrate", "system-run")
        btn.clicked.connect(self.main_window.migrate)
        migrate_layout.addWidget(btn)
        btn = create_button("Rollback", "edit-undo")
        btn.clicked.connect(self.main_window.rollback)
        migrate_layout.addWidget(btn)
        btn = create_button("Fresh", "view-refresh")
        btn.clicked.connect(self.main_window.fresh)
        migrate_layout.addWidget(btn)
        btn = create_button("Seed", "list-add")
        btn.clicked.connect(self.main_window.seed)
        migrate_layout.addWidget(btn)
        self.migrate_group.setLayout(migrate_layout)
        layout.addWidget(self.migrate_group)

        # --- Laravel Artisan Commands ---
        self.artisan_group = QGroupBox("Laravel Artisan")
        artisan_layout = QVBoxLayout()
        artisan_layout.setSpacing(10)
        self.optimize_btn = create_button("Optimize", "preferences-system")
        self.optimize_btn.clicked.connect(
            lambda: self.main_window.artisan("optimize")
        )
        self.config_clear_btn = create_button("Config Clear", "edit-clear")
        self.config_clear_btn.clicked.connect(
            lambda: self.main_window.artisan("config:clear")
        )
        artisan_layout.addWidget(self.optimize_btn)
        artisan_layout.addWidget(self.config_clear_btn)
        self.artisan_group.setLayout(artisan_layout)
        layout.addWidget(self.artisan_group)

        layout.addStretch(1)

        self.on_framework_changed(self.main_window.framework_choice)

    def on_framework_changed(self, text: str) -> None:
        visible = text == "Laravel"
        self.migrate_group.setVisible(visible)
        self.artisan_group.setVisible(visible)
