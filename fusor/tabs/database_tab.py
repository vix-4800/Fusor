from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class DatabaseTab(QWidget):
    """Tab with quick database helpers."""

    def __init__(self, main_window):
        """Create the database tools tab.

        Parameters
        ----------
        main_window : MainWindow
            Parent window exposing migration helpers.
        """
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        dbeaver_btn = QPushButton("Open in DBeaver")
        dbeaver_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dbeaver_btn.clicked.connect(lambda: print("Open in DBeaver clicked"))
        layout.addWidget(dbeaver_btn)

        dump_btn = QPushButton("Dump to SQL")
        dump_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dump_btn.clicked.connect(lambda: print("Dump to SQL clicked"))
        layout.addWidget(dump_btn)

        restore_btn = QPushButton("Restore dump")
        restore_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        restore_btn.clicked.connect(lambda: print("Restore dump clicked"))
        layout.addWidget(restore_btn)

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
