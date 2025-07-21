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
    QProgressDialog,
)
from PyQt6.QtCore import Qt
from typing import Optional

from . import APP_NAME


class WelcomeDialog(QDialog):
    """Dialog presented when no projects are configured."""

    def __init__(self, main_window) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle(f"Welcome to {APP_NAME}")
        self.progress_dialog: Optional[QProgressDialog] = None

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
        name, ok = QInputDialog.getText(
            self, "Create Project", "Project Name:"
        )
        if not ok or not name:
            return

        dest_base = QFileDialog.getExistingDirectory(self, "Select Destination")
        if not dest_base:
            return

        frameworks = ["Laravel", "Symfony", "Yii", "None"]
        fw_choice = getattr(self.main_window, "framework_choice", "Laravel")
        fw_index = frameworks.index(fw_choice) if fw_choice in frameworks else 0
        fw, ok = QInputDialog.getItem(
            self,
            "Create Project",
            "Framework:",
            frameworks,
            fw_index,
            editable=False,
        )
        if not ok or not fw:
            return

        dest = Path(dest_base) / name
        if dest.exists():
            QMessageBox.warning(self, "Create Project", "Destination already exists")
            return

        if fw == "Laravel":
            cmd = ["composer", "create-project", "laravel/laravel", str(dest)]
            cwd = dest_base
        elif fw == "Symfony":
            cmd = ["composer", "create-project", "symfony/skeleton", str(dest)]
            cwd = dest_base
        elif fw == "Yii":
            template = getattr(self.main_window, "yii_template", "basic")
            pkg = (
                "yiisoft/yii2-app-basic" if template == "basic" else "yiisoft/yii2-app-advanced"
            )
            cmd = ["composer", "create-project", pkg, str(dest)]
            cwd = dest_base
        else:
            dest.mkdir(parents=True, exist_ok=True)
            cmd = ["composer", "init", "-n"]
            cwd = str(dest)

        self.main_window.project_path = cwd
        self.main_window.framework_choice = fw
        if getattr(self.main_window, "framework_combo", None):
            self.main_window.framework_combo.setCurrentText(fw)

        self.setDisabled(True)
        self.main_window.setDisabled(True)
        dlg = QProgressDialog("Creating project...", None, 0, 0, self)
        dlg.setWindowTitle("Please Wait")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(0)
        dlg.setAutoClose(False)
        dlg.show()
        self.progress_dialog = dlg

        def finalize() -> None:
            if self.progress_dialog is not None:
                self.progress_dialog.hide()
                self.progress_dialog.deleteLater()
                self.progress_dialog = None
            self.main_window.set_current_project(str(dest))
            self.main_window.save_settings()
            self.main_window.setDisabled(False)
            self.setDisabled(False)
            self.accept()

        self.main_window.run_command(cmd, callback=finalize)

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
