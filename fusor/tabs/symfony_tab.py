from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QScrollArea,
)

from ..ui import create_button, CONTENT_MARGIN


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
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(20)

        self.console_group = QGroupBox("Symfony Console")
        console_layout = QVBoxLayout()
        console_layout.setSpacing(10)

        self.cache_clear_btn = create_button("Cache Clear", "view-refresh")
        self.cache_clear_btn.clicked.connect(
            lambda: self.main_window.symfony("cache:clear")
        )
        self.migrate_btn = create_button("Migrate", "system-run")
        self.migrate_btn.clicked.connect(
            lambda: self.main_window.symfony("doctrine:migrations:migrate")
        )
        self.status_btn = create_button("Migration Status", "dialog-information")
        self.status_btn.clicked.connect(
            lambda: self.main_window.symfony("doctrine:migrations:status")
        )
        self.make_migration_btn = create_button("Make Migration", "document-new")
        self.make_migration_btn.clicked.connect(
            lambda: self.main_window.symfony("make:migration")
        )

        console_layout.addWidget(self.cache_clear_btn)
        console_layout.addWidget(self.migrate_btn)
        console_layout.addWidget(self.status_btn)
        console_layout.addWidget(self.make_migration_btn)
        self.console_group.setLayout(console_layout)
        layout.addWidget(self.console_group)

        layout.addStretch(1)

        self.on_framework_changed(self.main_window.framework_choice)

    def on_framework_changed(self, text: str) -> None:
        visible = text == "Symfony"
        self.console_group.setVisible(visible)
