from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class ProjectTab(QWidget):
    """Tab with common project migration actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        migrate_btn = QPushButton("Migrate")
        migrate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        migrate_btn.clicked.connect(self.main_window.migrate)
        layout.addWidget(migrate_btn)

        rollback_btn = QPushButton("Rollback")
        rollback_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        rollback_btn.clicked.connect(self.main_window.rollback)
        layout.addWidget(rollback_btn)

        fresh_btn = QPushButton("Fresh")
        fresh_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        fresh_btn.clicked.connect(self.main_window.fresh)
        layout.addWidget(fresh_btn)

        seed_btn = QPushButton("Seed")
        seed_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        seed_btn.clicked.connect(self.main_window.seed)
        layout.addWidget(seed_btn)

        phpunit_btn = QPushButton("PHPUnit")
        phpunit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        phpunit_btn.clicked.connect(self.main_window.phpunit)
        layout.addWidget(phpunit_btn)
