from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QGroupBox,
    QFileDialog,
    QScrollArea,
)
from typing import Callable

from ..icons import get_icon


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
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(20)

        # --- SQL Tools Group ---
        tools_group = QGroupBox("SQL Tools")
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(10)

        self.dbeaver_btn = self._btn(
            "Open in DBeaver",
            self.open_dbeaver,
            icon="database",
        )
        self.dump_btn = self._btn(
            "Dump to SQL",
            self.dump_sql,
            icon="document-save",
        )
        self.restore_btn = self._btn(
            "Restore dump",
            self.restore_dump,
            icon="document-open",
        )

        tools_layout.addWidget(self.dbeaver_btn)
        tools_layout.addWidget(self.dump_btn)
        tools_layout.addWidget(self.restore_btn)

        tools_group.setLayout(tools_layout)
        outer_layout.addWidget(tools_group)

        outer_layout.addStretch(1)

    def on_framework_changed(self, _text: str) -> None:
        """Database tab has no framework specific controls."""
        pass

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

    def open_dbeaver(self) -> None:
        self.main_window.run_command(["dbeaver"], service=self.main_window.db_service)

    def dump_sql(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save SQL Dump", filter="SQL Files (*.sql)"
        )
        if path:
            self.main_window.run_command([
                "mysqldump",
                "--result-file",
                path,
            ], service=self.main_window.db_service)

    def restore_dump(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select SQL Dump", filter="SQL Files (*.sql)"
        )
        if path:
            self.main_window.run_command(["mysql", path], service=self.main_window.db_service)
