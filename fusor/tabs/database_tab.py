from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFileDialog,
    QScrollArea,
    QComboBox,
    QLabel,
    QHBoxLayout,
)

from ..ui import create_button, CONTENT_MARGIN


class DatabaseTab(QWidget):
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

        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        outer_layout.setSpacing(20)

        # --- SQL Tools Group ---
        tools_group = QGroupBox("SQL Tools")
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(10)

        combo_row = QHBoxLayout()
        combo_label = QLabel("Database:")
        self.db_combo = QComboBox()
        self.db_combo.addItems(["MySQL/MariaDB", "PostgreSQL"])
        combo_row.addWidget(combo_label)
        combo_row.addWidget(self.db_combo)
        tools_layout.addLayout(combo_row)

        self.dbeaver_btn = create_button("Open in DBeaver", "database")
        self.dbeaver_btn.clicked.connect(self.open_dbeaver)
        self.dump_btn = create_button("Dump to SQL", "document-save")
        self.dump_btn.clicked.connect(self.dump_sql)
        self.restore_btn = create_button("Restore dump", "document-open")
        self.restore_btn.clicked.connect(self.restore_dump)

        tools_layout.addWidget(self.dbeaver_btn)
        tools_layout.addWidget(self.dump_btn)
        tools_layout.addWidget(self.restore_btn)

        tools_group.setLayout(tools_layout)
        outer_layout.addWidget(tools_group)

        outer_layout.addStretch(1)

    def on_framework_changed(self, _text: str) -> None:
        """Database tab has no framework specific controls."""
        pass

    def open_dbeaver(self) -> None:
        self.main_window.run_command(["dbeaver"], service=self.main_window.db_service)

    def dump_sql(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save SQL Dump", filter="SQL Files (*.sql)"
        )
        if path:
            if self.db_combo.currentText() == "PostgreSQL":
                cmd = ["pg_dump", "-f", path]
            else:
                cmd = ["mysqldump", "--result-file", path]
            self.main_window.run_command(cmd, service=self.main_window.db_service)

    def restore_dump(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select SQL Dump", filter="SQL Files (*.sql)"
        )
        if path:
            if self.db_combo.currentText() == "PostgreSQL":
                cmd = ["psql", "-f", path]
            else:
                cmd = ["mysql", path]
            self.main_window.run_command(cmd, service=self.main_window.db_service)
