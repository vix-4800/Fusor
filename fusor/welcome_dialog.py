from __future__ import annotations

from pathlib import Path
import subprocess
import logging

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)

from . import APP_NAME

logger = logging.getLogger(__name__)


class WelcomeDialog(QDialog):
    """Dialog presented when no projects are configured."""

    def __init__(self, main_window) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle(f"Welcome to {APP_NAME}")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a project to get started:"))

        add_btn = QPushButton("Add Project")
        add_btn.clicked.connect(self.add_project)
        layout.addWidget(add_btn)

        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_project)
        layout.addWidget(create_btn)

        clone_btn = QPushButton("Clone from Git")
        clone_btn.clicked.connect(self.clone_project)
        layout.addWidget(clone_btn)

    # ------------------------------------------------------------------
    def add_project(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.main_window.set_current_project(path)
            self.main_window.save_settings()
            self.accept()

    def create_project(self) -> None:  # pragma: no cover - not implemented yet
        QMessageBox.information(self, "Create Project", "Not implemented yet")

    def clone_project(self) -> None:
        url, ok = QInputDialog.getText(self, "Clone from Git", "Repository URL:")
        if not ok or not url:
            return

        dest_base = QFileDialog.getExistingDirectory(self, "Select Destination")
        if not dest_base:
            return

        name, ok = QInputDialog.getText(
            self, "Clone from Git", "Project Directory Name:"
        )
        if not ok or not name:
            return

        dest = Path(dest_base) / name
        if dest.exists():
            QMessageBox.warning(self, "Clone", "Destination already exists")
            return

        try:
            check = subprocess.run(
                ["git", "ls-remote", url], capture_output=True, text=True
            )
            if check.returncode != 0:
                QMessageBox.warning(self, "Clone", "Invalid repository URL")
                return
        except FileNotFoundError:  # pragma: no cover
            QMessageBox.warning(self, "Clone", "git executable not found")
            return

        subprocess.run(["git", "clone", url, str(dest)])
        self.main_window.set_current_project(str(dest))
        self.main_window.save_settings()
        self.accept()
