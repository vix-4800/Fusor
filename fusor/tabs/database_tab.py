from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
    QFileDialog,
)

class DatabaseTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(20)

        # --- SQL Tools Group ---
        tools_group = QGroupBox("SQL Tools")
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(10)

        self.dbeaver_btn = self._btn("🧩 Open in DBeaver", self.open_dbeaver)
        self.dump_btn = self._btn("💾 Dump to SQL", self.dump_sql)
        self.restore_btn = self._btn("📂 Restore dump", self.restore_dump)

        tools_layout.addWidget(self.dbeaver_btn)
        tools_layout.addWidget(self.dump_btn)
        tools_layout.addWidget(self.restore_btn)

        tools_group.setLayout(tools_layout)
        outer_layout.addWidget(tools_group)

        # --- Migrations Group ---
        migrate_group = QGroupBox("Laravel Migrations")
        migrate_layout = QVBoxLayout()
        migrate_layout.setSpacing(10)

        migrate_layout.addWidget(self._btn("Migrate", self.main_window.migrate))
        migrate_layout.addWidget(self._btn("↩ Rollback", self.main_window.rollback))
        migrate_layout.addWidget(self._btn("Fresh", self.main_window.fresh))
        migrate_layout.addWidget(self._btn("Seed", self.main_window.seed))

        migrate_group.setLayout(migrate_layout)
        outer_layout.addWidget(migrate_group)

        outer_layout.addStretch(1)

    def _btn(self, text, slot):
        btn = QPushButton(text)
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def open_dbeaver(self):
        self.main_window.run_command(["dbeaver"])

    def dump_sql(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save SQL Dump", filter="SQL Files (*.sql)")
        if path:
            self.main_window.run_command(["mysqldump", "--result-file", path])

    def restore_dump(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select SQL Dump", filter="SQL Files (*.sql)")
        if path:
            self.main_window.run_command(["mysql", path])
