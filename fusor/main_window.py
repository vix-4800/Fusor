import sys
import os
import subprocess
import concurrent.futures
import builtins
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
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

# allow tests to monkeypatch file operations easily
open = builtins.open

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusor – Laravel/PHP QA Toolbox")
        self.resize(1024, 768)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }

            QTabWidget::pane {
                border: none;
            }

            QWidget {
                background-color: #1e1e1e;
                color: #dddddd;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 14px;
            }

            QPushButton {
                background-color: #2e7d32;
                color: #ffffff;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #388e3c;
            }

            QPushButton:pressed {
                background-color: #1b5e20;
            }

            QTextEdit, QLineEdit {
                background-color: #2c2c2c;
                color: #eeeeee;
                padding: 8px;
                border: 1px solid #444444;
                border-radius: 6px;
                font-family: monospace;
            }

            QComboBox {
                background-color: #2c2c2c;
                color: #eeeeee;
                padding: 6px;
                border: 1px solid #444444;
                border-radius: 6px;
            }

            QComboBox QAbstractItemView {
                background-color: #2c2c2c;
                selection-background-color: #388e3c;
                selection-color: white;
            }

            QTabBar::tab {
                background: transparent;
                color: #888888;
                padding: 12px;
                border: none;
            }

            QTabBar::tab:selected {
                color: #4caf50;
                font-weight: bold;
            }

            QScrollBar:vertical {
                background: #2c2c2c;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #666;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.tabs = QTabWidget()
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self.tabs)

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setMaximumHeight(180)
        main_layout.addWidget(self.output_view)

        self.setCentralWidget(central_widget)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.server_process = None

        # Redirect stdout to the output view
        self._stdout_logger = QTextEditLogger(self.output_view, sys.stdout)
        sys.stdout = self._stdout_logger

        # Directory containing project files and PHP executable path
        self.project_path = ""
        self.framework_choice = "Laravel"
        self.php_path = "php"
        self.php_service = "php"
        self.server_port = 8000
        self.use_docker = False
        self.yii_template = "basic"
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
        self.project_path_edit.setText(self.project_path)
        if self.framework_choice in [self.framework_combo.itemText(i) for i in range(self.framework_combo.count())]:
            self.framework_combo.setCurrentText(self.framework_choice)

        if self.project_path:
            self.git_tab.load_branches()
        else:
            QTimer.singleShot(0, self.ask_project_path)

    def load_config(self):
        data = load_config()
        self.project_path = data.get("project_path", self.project_path)
        self.framework_choice = data.get("framework", self.framework_choice)
        self.php_path = data.get("php_path", self.php_path)
        self.php_service = data.get("php_service", self.php_service)
        self.server_port = data.get("server_port", self.server_port)
        self.use_docker = data.get("use_docker", self.use_docker)
        self.yii_template = data.get("yii_template", self.yii_template)

    def run_command(self, command):
        if self.use_docker and not (
            len(command) >= 2 and command[0] == "docker" and command[1] == "compose"
        ):
            command = [
                "docker",
                "compose",
                "exec",
                "-T",
                self.php_service,
                *command,
            ]
        cwd = self.project_path if self.use_docker else None

        def task():
            try:
                result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(result.stderr.strip())
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")

        print(f"$ {' '.join(command)}")
        self.executor.submit(task)

    def ensure_project_path(self):
        if not self.project_path:
            print("Project path not set")
            self.close()
            return False
        return True

    def ask_project_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.project_path = path
            if hasattr(self, "project_path_edit"):
                self.project_path_edit.setText(path)
        if self.ensure_project_path():
            # update git branch list now that the project path is set
            if hasattr(self, "git_tab"):
                self.git_tab.load_branches()

    def current_framework(self):
        return self.framework_combo.currentText() if hasattr(self, "framework_combo") else "None"

    def refresh_logs(self):
        if not self.ensure_project_path():
            return

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
        project_path = self.project_path_edit.text()
        framework = self.framework_combo.currentText()
        php_path = self.php_path_edit.text()
        php_service = self.php_service_edit.text() if hasattr(self, "php_service_edit") else self.php_service
        port_text = self.server_port_edit.text() if hasattr(self, "server_port_edit") else str(self.server_port)
        use_docker = self.docker_checkbox.isChecked()
        yii_template = self.yii_template_combo.currentText() if hasattr(self, "yii_template_combo") else self.yii_template

        if (
            not project_path
            or (not php_path and not use_docker)
            or (use_docker and not php_service)
            or not port_text.isdigit()
        ):
            QMessageBox.warning(self, "Invalid settings", "All settings fields must be filled out.")
            print("Failed to save settings: one or more fields were empty")
            return

        if not os.path.isdir(project_path):
            QMessageBox.warning(self, "Invalid project path", "The specified project path does not exist.")
            print(f"Failed to save settings: directory does not exist - {project_path}")
            return

        if not use_docker and not os.path.isfile(php_path):
            QMessageBox.warning(self, "Invalid PHP path", "The specified PHP executable was not found.")
            print(f"Failed to save settings: php not found - {php_path}")
            return

        server_port = int(port_text)

        self.project_path = project_path
        self.framework_choice = framework
        self.php_path = php_path
        self.php_service = php_service or self.php_service
        self.server_port = server_port
        self.use_docker = use_docker
        self.yii_template = yii_template

        data = {
            "project_path": project_path,
            "framework": framework,
            "php_path": php_path,
            "php_service": php_service,
            "server_port": server_port,
            "use_docker": use_docker,
            "yii_template": yii_template,
        }
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")

        print("Settings saved!")

        if hasattr(self, "git_tab"):
            self.git_tab.load_branches()

    def artisan(self, *args):
        self.ensure_project_path()
        artisan_file = os.path.join(self.project_path, "artisan")
        self.run_command([self.php_path, artisan_file, *args])

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

    def phpunit(self):
        self.ensure_project_path()
        phpunit_file = os.path.join(self.project_path, "vendor", "bin", "phpunit")
        self.run_command([self.php_path, phpunit_file])

    def start_project(self):
        if self.use_docker:
            self.run_command(["docker", "compose", "up", "-d"])
            return

        if self.server_process and self.server_process.poll() is None:
            print("Project already running")
            return

        if not self.ensure_project_path():
            return

        if self.current_framework() == "Laravel":
            artisan_file = os.path.join(self.project_path, "artisan")
            command = [self.php_path, artisan_file, "serve"]
        else:
            # fallback generic PHP server
            command = [
                self.php_path,
                "-S",
                f"localhost:{self.server_port}",
                "-t",
                os.path.join(self.project_path, "public"),
            ]

        print(f"$ {' '.join(command)}")
        try:
            self.server_process = subprocess.Popen(
                command,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            def stream():
                assert self.server_process is not None
                for line in self.server_process.stdout:
                    print(line.rstrip())

            self.executor.submit(stream)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")

    def stop_project(self):
        if self.use_docker:
            self.run_command(["docker", "compose", "down"])
            return

        if self.server_process and self.server_process.poll() is None:
            print("Stopping project...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
        else:
            print("Project is not running")

    def closeEvent(self, event):
        if self.server_process and self.server_process.poll() is None:
            if hasattr(self.server_process, "terminate"):
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if hasattr(self.server_process, "kill"):
                        self.server_process.kill()
            self.server_process = None
        self.executor.shutdown(wait=False)
        super().closeEvent(event)
