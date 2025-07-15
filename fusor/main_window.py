import sys
import os
import subprocess
import signal
import concurrent.futures
import builtins
import shutil
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QInputDialog,
)
from PyQt6.QtCore import QTimer

from .config import load_config, save_config, DEFAULT_PROJECT_SETTINGS
from .qtextedit_logger import QTextEditLogger

from .tabs.project_tab import ProjectTab
from .tabs.git_tab import GitTab
from .tabs.database_tab import DatabaseTab
from .tabs.framework_tab import FrameworkTab
from .tabs.docker_tab import DockerTab
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

            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }

            QTextEdit, QLineEdit {
                background-color: #2c2c2c;
                color: #eeeeee;
                padding: 8px;
                border: 1px solid #444444;
                border-radius: 6px;
                font-family: monospace;
            }

            QTextEdit:disabled, QLineEdit:disabled, QComboBox:disabled {
                background-color: #3a3a3a;
                color: #777777;
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

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.help_button)
        main_layout.addLayout(header_layout)

        main_layout.addWidget(self.tabs)

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setMaximumHeight(180)
        main_layout.addWidget(self.output_view)

        self.clear_output_button = QPushButton("Clear Output")
        self.clear_output_button.clicked.connect(self.clear_output)
        main_layout.addWidget(self.clear_output_button)

        self.setCentralWidget(central_widget)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.server_process = None
        self.settings_dirty = False

        # Redirect stdout to the output view
        self._stdout_logger = QTextEditLogger(self.output_view, sys.stdout)
        sys.stdout = self._stdout_logger

        # Directory containing project files and PHP executable path
        self.project_path = ""
        self.projects: list[str] = []
        self.framework_choice = "Laravel"
        self.php_path = "php"
        self.php_service = "php"
        self.server_port = 8000
        self.use_docker = False
        self.compose_files: list[str] = []
        self.yii_template = "basic"
        self.log_path = os.path.join("storage", "logs", "laravel.log")
        self.git_remote = ""
        self.load_config()

        # initialize tabs
        self.project_tab = ProjectTab(self)
        self.tabs.addTab(self.project_tab, "Project")

        self.git_tab = GitTab(self)
        self.tabs.addTab(self.git_tab, "Git")

        self.database_tab = DatabaseTab(self)
        self.tabs.addTab(self.database_tab, "Database")

        self.framework_tab = FrameworkTab(self)
        self.framework_index = self.tabs.addTab(self.framework_tab, "Framework")

        self.docker_tab = DockerTab(self)
        self.docker_index = self.tabs.addTab(self.docker_tab, "Docker")

        self.logs_tab = LogsTab(self)
        self.tabs.addTab(self.logs_tab, "Logs")

        self.settings_tab = SettingsTab(self)
        self.settings_index = self.tabs.addTab(self.settings_tab, "Settings")
        self.update_settings_tab_title()

        # docker tab availability
        self.tabs.setTabVisible(self.docker_index, self.use_docker)
        self.tabs.setTabEnabled(self.docker_index, self.use_docker)

        # framework tab availability
        show_fw = self.framework_choice != "None"
        self.tabs.setTabVisible(self.framework_index, show_fw)
        self.tabs.setTabEnabled(self.framework_index, show_fw)

        # populate settings widgets with loaded values
        if hasattr(self, "project_combo"):
            self.project_combo.setCurrentText(self.project_path)
        if self.framework_choice in [self.framework_combo.itemText(i) for i in range(self.framework_combo.count())]:
            self.framework_combo.setCurrentText(self.framework_choice)

        if self.project_path:
            self.git_tab.load_branches()
            self.git_tab.load_remote_branches()
        else:
            QTimer.singleShot(0, self.choose_project)

    def load_config(self):
        data = load_config()
        self.projects = data.get("projects", [])
        self.project_path = data.get("current_project", self.project_path)
        if not self.projects and data.get("project_path"):
            self.projects = [data["project_path"]]
        if not self.project_path and self.projects:
            self.project_path = self.projects[0]

        settings = data.get("project_settings", {}).get(self.project_path, {})

        self.framework_choice = settings.get(
            "framework", data.get("framework", self.framework_choice)
        )
        self.php_path = settings.get("php_path", data.get("php_path", self.php_path))
        self.php_service = settings.get(
            "php_service", data.get("php_service", self.php_service)
        )
        self.server_port = settings.get(
            "server_port", data.get("server_port", self.server_port)
        )
        self.use_docker = settings.get(
            "use_docker", data.get("use_docker", self.use_docker)
        )
        self.yii_template = settings.get(
            "yii_template", data.get("yii_template", self.yii_template)
        )
        self.log_path = settings.get("log_path", data.get("log_path", self.log_path))
        self.git_remote = settings.get(
            "git_remote", data.get("git_remote", self.git_remote)
        )
        self.compose_files = settings.get(
            "compose_files", data.get("compose_files", self.compose_files)
        )

    def _compose_prefix(self) -> list[str]:
        prefix = ["docker", "compose"]
        for f in self.compose_files:
            prefix.extend(["-f", f])
        return prefix

    def update_settings_tab_title(self):
        if hasattr(self, "settings_index"):
            label = "Settings*" if self.settings_dirty else "Settings"
            self.tabs.setTabText(self.settings_index, label)

    def mark_settings_dirty(self):
        if not self.settings_dirty:
            self.settings_dirty = True
            self.update_settings_tab_title()

    def mark_settings_saved(self):
        if self.settings_dirty:
            self.settings_dirty = False
            self.update_settings_tab_title()

    def apply_project_settings(self):
        """Load settings for the current project and update widgets."""
        data = load_config()
        settings = DEFAULT_PROJECT_SETTINGS.copy()
        settings.update(data.get("project_settings", {}).get(self.project_path, {}))

        self.framework_choice = settings["framework"]
        self.php_path = settings["php_path"]
        self.php_service = settings["php_service"]
        self.server_port = settings["server_port"]
        self.use_docker = settings["use_docker"]
        self.yii_template = settings["yii_template"]
        self.log_path = settings["log_path"]
        self.git_remote = settings["git_remote"]
        self.compose_files = settings["compose_files"]

        if hasattr(self, "framework_combo"):
            self.framework_combo.setCurrentText(self.framework_choice)
        if hasattr(self, "php_path_edit"):
            self.php_path_edit.setText(self.php_path)
        if hasattr(self, "php_service_edit"):
            self.php_service_edit.setText(self.php_service)
        if hasattr(self, "server_port_edit"):
            self.server_port_edit.setText(str(self.server_port))
        if hasattr(self, "docker_checkbox"):
            self.docker_checkbox.setChecked(self.use_docker)
        if hasattr(self, "yii_template_combo"):
            self.yii_template_combo.setCurrentText(self.yii_template)
        if hasattr(self, "log_path_edit"):
            self.log_path_edit.setText(self.log_path)
        if hasattr(self, "remote_combo"):
            remotes = self.git_tab.get_remotes() if hasattr(self, "git_tab") else []
            if self.git_remote and self.git_remote not in remotes:
                self.remote_combo.addItem(self.git_remote)
            self.remote_combo.setCurrentText(self.git_remote)
        if hasattr(self, "compose_files_edit"):
            self.compose_files_edit.setText(";".join(self.compose_files))

        self.mark_settings_saved()

    def run_command(self, command):
        if self.use_docker:
            if len(command) >= 2 and command[0] == "docker" and command[1] == "compose":
                command = self._compose_prefix() + command[2:]
            else:
                command = self._compose_prefix() + [
                    "exec",
                    "-T",
                    self.php_service,
                    *command,
                ]
            cwd = self.project_path
        else:
            cwd = self.project_path

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

    def set_current_project(self, path: str):
        if not path:
            return
        self.project_path = path
        if path not in self.projects:
            self.projects.append(path)
        if hasattr(self, "project_combo"):
            self.project_combo.blockSignals(True)
            if path not in [self.project_combo.itemText(i) for i in range(self.project_combo.count())]:
                self.project_combo.addItem(path)
            self.project_combo.setCurrentText(path)
            self.project_combo.blockSignals(False)
        if hasattr(self, "git_tab"):
            self.git_tab.load_branches()
            self.git_tab.load_remote_branches()

        self.apply_project_settings()

    def add_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.set_current_project(path)
            self.save_settings()

    def choose_project(self):
        if not self.projects:
            self.add_project()
            return
        project, ok = QInputDialog.getItem(
            self,
            "Choose Project",
            "Select project:",
            self.projects,
            editable=False,
        )
        if ok and project:
            self.set_current_project(project)

    def current_framework(self):
        return self.framework_combo.currentText() if hasattr(self, "framework_combo") else "None"

    def refresh_logs(self):
        if not self.ensure_project_path():
            return

        framework = self.current_framework()
        log_contents = ""
        if framework == "Laravel":
            log_file = self.log_path
            if not os.path.isabs(log_file):
                log_file = os.path.join(self.project_path, log_file)
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
        project_path = self.project_combo.currentText() if hasattr(self, "project_combo") else self.project_path
        framework = self.framework_combo.currentText()
        php_path = self.php_path_edit.text()
        php_service = self.php_service_edit.text() if hasattr(self, "php_service_edit") else self.php_service
        port_text = self.server_port_edit.text() if hasattr(self, "server_port_edit") else str(self.server_port)
        use_docker = self.docker_checkbox.isChecked()
        yii_template = self.yii_template_combo.currentText() if hasattr(self, "yii_template_combo") else self.yii_template
        log_path = self.log_path_edit.text() if hasattr(self, "log_path_edit") else self.log_path
        git_remote = self.remote_combo.currentText() if hasattr(self, "remote_combo") else self.git_remote
        compose_text = self.compose_files_edit.text() if hasattr(self, "compose_files_edit") else ";".join(self.compose_files)

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

        if not use_docker:
            valid_path = os.path.isfile(php_path)
            if not valid_path:
                valid_path = shutil.which(php_path) is not None
            if not valid_path:
                QMessageBox.warning(self, "Invalid PHP path", "The specified PHP executable was not found.")
                print(f"Failed to save settings: php not found - {php_path}")
                return

        server_port = int(port_text)

        self.project_path = project_path
        if project_path not in self.projects:
            self.projects.append(project_path)
        self.framework_choice = framework
        self.php_path = php_path
        self.php_service = php_service or self.php_service
        self.server_port = server_port
        self.use_docker = use_docker
        self.yii_template = yii_template
        self.log_path = log_path
        self.git_remote = git_remote
        self.compose_files = [f for f in compose_text.split(";") if f]

        data = load_config()
        settings = data.get("project_settings", {})
        settings[project_path] = {
            "framework": framework,
            "php_path": php_path,
            "php_service": php_service,
            "server_port": server_port,
            "use_docker": use_docker,
            "yii_template": yii_template,
            "log_path": log_path,
            "git_remote": git_remote,
            "compose_files": self.compose_files,
        }
        data.update({
            "projects": self.projects,
            "current_project": project_path,
            "project_settings": settings,
        })
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")

        print("Settings saved!")
        self.mark_settings_saved()

        if hasattr(self, "git_tab"):
            self.git_tab.load_branches()
            self.git_tab.load_remote_branches()

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
                self.project_path, # os.path.join(self.project_path, "public")
            ]

        print(f"$ {' '.join(command)}")
        try:
            popen_args = {
                "cwd": self.project_path,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
            }
            if os.name == "nt":
                popen_args["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                popen_args["start_new_session"] = True

            self.server_process = subprocess.Popen(command, **popen_args)

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
            try:
                if os.name == "nt":
                    if hasattr(self.server_process, "send_signal"):
                        self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    if hasattr(self.server_process, "pid"):
                        os.killpg(self.server_process.pid, signal.SIGINT)
                if hasattr(self.server_process, "wait"):
                    self.server_process.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                if hasattr(self.server_process, "kill"):
                    self.server_process.kill()
            self.server_process = None
        else:
            print("Project is not running")

    def closeEvent(self, event):
        if self.server_process and self.server_process.poll() is None:
            try:
                if os.name == "nt":
                    if hasattr(self.server_process, "send_signal"):
                        self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    if hasattr(self.server_process, "pid"):
                        os.killpg(self.server_process.pid, signal.SIGINT)
                if hasattr(self.server_process, "wait"):
                    self.server_process.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                if hasattr(self.server_process, "kill"):
                    self.server_process.kill()
            self.server_process = None
        self.executor.shutdown(wait=False)
        super().closeEvent(event)

    def show_about_dialog(self):
        from .about_dialog import AboutDialog

        dlg = AboutDialog(self)
        dlg.exec()

    def clear_output(self):
        self.output_view.clear()
