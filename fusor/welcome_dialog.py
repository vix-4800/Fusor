from __future__ import annotations

from pathlib import Path
import subprocess

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

    def create_project(self) -> None:
        dest_base = QFileDialog.getExistingDirectory(self, "Select Destination")
        if not dest_base:
            return

        name, ok = QInputDialog.getText(
            self, "Create Project", "Project Directory Name:"
        )
        if not ok or not name:
            return

        dest = Path(dest_base) / name
        if dest.exists():
            QMessageBox.warning(self, "Create Project", "Destination already exists")
            return

        fw = getattr(self.main_window, "framework_choice", "Laravel")
        if fw == "Laravel":
            cmd = ["composer", "create-project", "laravel/laravel", str(dest)]
        elif fw == "Symfony":
            cmd = ["composer", "create-project", "symfony/skeleton", str(dest)]
        elif fw == "Yii":
            template = getattr(self.main_window, "yii_template", "basic")
            pkg = (
                "yiisoft/yii2-app-basic"
                if template == "basic"
                else "yiisoft/yii2-app-advanced"
            )
            cmd = ["composer", "create-project", pkg, str(dest)]
        else:
            dest.mkdir(parents=True, exist_ok=True)
            cmd = ["composer", "init", "-n"]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=dest if cmd[1] == "init" else None,
            )
        except FileNotFoundError:
            QMessageBox.warning(self, "Create Project", "composer executable not found")
            return

        if res.returncode != 0:
            QMessageBox.warning(
                self,
                "Create Project",
                res.stderr or "Failed to create project",
            )
            return

        self.main_window.set_current_project(str(dest))
        self.main_window.save_settings()
        self.accept()

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
