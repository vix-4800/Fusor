import sys
import os
import subprocess
import concurrent.futures
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

from .config import load_config, save_config
from .qtextedit_logger import QTextEditLogger

from .tabs.project_tab import ProjectTab
from .tabs.git_tab import GitTab
from .tabs.database_tab import DatabaseTab
from .tabs.logs_tab import LogsTab
from .tabs.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    """Main application window hosting all feature tabs."""
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

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        # Redirect stdout to the output view
        self._stdout_logger = QTextEditLogger(self.output_view, sys.stdout)
        sys.stdout = self._stdout_logger

        # Directory containing php and artisan executables
        self.project_path = ""
        self.git_url = ""
        self.framework_choice = "Laravel"
        self.load_config()

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

        # populate settings widgets with loaded values
        self.git_url_edit.setText(self.git_url)
        self.project_path_edit.setText(self.project_path)
        if self.framework_choice in [self.framework_combo.itemText(i) for i in range(self.framework_combo.count())]:
            self.framework_combo.setCurrentText(self.framework_choice)

        if not self.project_path:
            QTimer.singleShot(0, self.ask_project_path)

    def load_config(self):
        """Load saved configuration values into the instance."""
        data = load_config()
        self.project_path = data.get("project_path", self.project_path)
        self.git_url = data.get("git_url", "")
        self.framework_choice = data.get("framework", self.framework_choice)

    def run_command(self, command):
        """Execute *command* asynchronously and stream output to the log view."""

        def task():
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(result.stderr.strip())
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")

        print(f"$ {' '.join(command)}")
        self.executor.submit(task)

    def ensure_project_path(self):
        """Warn and close the app if the project path is not set."""
        if not self.project_path:
            print("Project path not set")
            self.close()
            return False
        return True

    def ask_project_path(self):
        """Prompt the user for a project path on startup."""
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.project_path = path
            if hasattr(self, "project_path_edit"):
                self.project_path_edit.setText(path)
        self.ensure_project_path()

    def current_framework(self):
        return self.framework_combo.currentText() if hasattr(self, "framework_combo") else "None"

    def refresh_logs(self):
        print("Refresh logs clicked")

        self.ensure_project_path()

        framework = self.current_framework()
        log_contents = ""
        if framework == "Laravel":
            log_file = os.path.join(
                self.project_path, "storage", "logs", "laravel.log"
            )
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        log_contents = f.read()
                except OSError as e:
                    log_contents = f"Failed to read log file: {e}"
            else:
                log_contents = f"Log file not found: {log_file}"
        else:
            log_contents = f"Logs not implemented for {framework}"

        self.log_view.setPlainText(log_contents.strip())

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
        self.git_url = git_url
        self.framework_choice = framework

        data = {
            "git_url": git_url,
            "project_path": project_path,
            "framework": framework,
        }
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")

        print(f"Settings saved!")

    def artisan(self, *args):
        self.ensure_project_path()
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

    def closeEvent(self, event):
        """Shutdown background executor before closing."""
        self.executor.shutdown(wait=False)
        super().closeEvent(event)
