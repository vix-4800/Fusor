import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QHBoxLayout,
    QTextEdit,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import QTimer

from .tabs.project_tab import ProjectTab
from .tabs.git_tab import GitTab
from .tabs.database_tab import DatabaseTab
from .tabs.logs_tab import LogsTab
from .tabs.settings_tab import SettingsTab


class QTextEditLogger:
    """Redirect writes to both stdout and a QTextEdit widget."""

    def __init__(self, text_edit, original_stdout):
        self.text_edit = text_edit
        self.original_stdout = original_stdout

    def write(self, msg):
        if msg.rstrip():
            self.text_edit.append(msg.rstrip())
        self.original_stdout.write(msg)

    def flush(self):
        self.original_stdout.flush()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusor – Laravel/PHP QA Toolbox")
        self.resize(1024, 768)

        self.tabs = QTabWidget()
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.output_view)
        self.setCentralWidget(central_widget)

        # Redirect stdout to the output view
        self._stdout_logger = QTextEditLogger(self.output_view, sys.stdout)
        sys.stdout = self._stdout_logger

        # Directory containing php and artisan executables
        self.project_path = ""

        # initialize tabs
        self.project_tab = ProjectTab(self)
        self.tabs.addTab(self.project_tab, "Project")

        self.git_tab = GitTab(self)
        self.tabs.addTab(self.git_tab, "Git")

        self.database_tab = DatabaseTab(self)
        self.tabs.addTab(self.database_tab, "Database")

        self.logs_tab = LogsTab(self)
        self.tabs.addTab(self.logs_tab, "Logs")

        self.settings_tab = SettingsTab(self)
        self.tabs.addTab(self.settings_tab, "Settings")

        QTimer.singleShot(0, self.ask_project_path)

    # logic helpers
    def run_command(self, command):
        """Run a shell command and print its output."""
        print(f"$ {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip())
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")

    def ensure_project_path(self):
        """Return True if project path is set else warn the user."""
        if not self.project_path:
            QMessageBox.warning(
                self,
                "Project Path Missing",
                "Please set the project path in Settings.",
            )
            print("Project path not set")
            return False
        return True

    def ask_project_path(self):
        """Prompt the user for a project path on startup."""
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.project_path = path
            if hasattr(self, "project_path_edit"):
                self.project_path_edit.setText(path)

    def current_framework(self):
        return self.framework_combo.currentText() if hasattr(self, "framework_combo") else "None"

    def refresh_logs(self):
        print("Refresh logs clicked")
        self.log_view.setPlainText(
            "Example log line 1\nExample log line 2\nExample log line 3"
        )

    def save_settings(self):
        git_url = self.git_url_edit.text()
        project_path = self.project_path_edit.text()
        framework = self.framework_combo.currentText()

        if not git_url or not project_path:
            QMessageBox.warning(self, "Invalid settings", "All settings fields must be filled out.")
            print("Failed to save settings: one or more fields were empty")
            return

        if not os.path.isdir(project_path):
            QMessageBox.warning(self, "Invalid PHP path", "The specified PHP path does not exist.")
            print(f"Failed to save settings: directory does not exist - {project_path}")
            return

        self.project_path = project_path

        print(
            f"Settings saved: Git URL={git_url}, PHP Path={project_path}, Framework={framework}"
        )

    def artisan(self, *args):
        if not self.ensure_project_path():
            return
        artisan_file = os.path.join(self.project_path, "artisan")
        self.run_command(["php", artisan_file, *args])

    def migrate(self):
        if self.current_framework() == "Laravel":
            self.artisan("migrate")
        else:
            print(f"Migrate not implemented for {self.current_framework()}")

    def rollback(self):
        if self.current_framework() == "Laravel":
            self.artisan("migrate:rollback")
        else:
            print(f"Rollback not implemented for {self.current_framework()}")

    def fresh(self):
        if self.current_framework() == "Laravel":
            self.artisan("migrate:fresh")
        else:
            print(f"Fresh not implemented for {self.current_framework()}")

    def seed(self):
        if self.current_framework() == "Laravel":
            self.artisan("db:seed")
        else:
            print(f"Seed not implemented for {self.current_framework()}")

