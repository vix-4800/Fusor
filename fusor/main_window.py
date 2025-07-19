import sys
import os
from pathlib import Path
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
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from PyQt6.QtWidgets import (
        QComboBox,
        QLineEdit,
        QSpinBox,
        QCheckBox,
    )
    from PyQt6.QtGui import QCloseEvent
from .icons import get_icon
from . import APP_NAME

from .config import (
    load_config,
    save_config,
    DEFAULT_PROJECT_SETTINGS,
    DEFAULT_MAX_LOG_LINES,
)
from .qtextedit_logger import QTextEditLogger
from .welcome_dialog import WelcomeDialog

from .tabs.project_tab import ProjectTab
from .tabs.git_tab import GitTab
from .tabs.database_tab import DatabaseTab
from .tabs.laravel_tab import LaravelTab
from .tabs.symfony_tab import SymfonyTab
from .tabs.yii_tab import YiiTab
from .tabs.docker_tab import DockerTab
from .tabs.logs_tab import LogsTab
from .tabs.terminal_tab import TerminalTab
from .tabs.settings_tab import SettingsTab

# allow tests to monkeypatch file operations easily
open = builtins.open

DARK_STYLESHEET = """
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

    QTextEdit, QLineEdit, QSpinBox {
        background-color: #2c2c2c;
        color: #eeeeee;
        padding: 8px;
        border: 1px solid #444444;
        border-radius: 6px;
        font-family: monospace;
    }

    QTextEdit:disabled, QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
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
"""

LIGHT_STYLESHEET = """
    QMainWindow {
        background-color: #f9f9f9;
    }

    QTabWidget::pane {
        border: none;
    }

    QWidget {
        background-color: #f9f9f9;
        color: #1e1e1e;
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 14px;
    }

    QPushButton {
        background-color: #007bff;
        color: #ffffff;
        padding: 8px 16px;
        border: none;
        border-radius: 6px;
        font-weight: 500;
    }

    QPushButton:hover {
        background-color: #339cff;
    }

    QPushButton:pressed {
        background-color: #0062cc;
    }

    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #a0a0a0;
    }

    QTextEdit, QLineEdit, QSpinBox {
        background-color: #ffffff;
        color: #1e1e1e;
        padding: 8px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        font-family: monospace;
    }

    QTextEdit:disabled, QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
        background-color: #f0f0f0;
        color: #999999;
    }

    QComboBox {
        background-color: #ffffff;
        color: #1e1e1e;
        padding: 6px;
        border: 1px solid #cccccc;
        border-radius: 6px;
    }

    QComboBox QAbstractItemView {
        background-color: #ffffff;
        selection-background-color: #cce5ff;
        selection-color: #000000;
    }

    QTabBar::tab {
        background: transparent;
        color: #555555;
        padding: 12px;
        border: none;
    }

    QTabBar::tab:selected {
        color: #007bff;
        font-weight: bold;
    }

    QScrollBar:vertical {
        background: #f5f5f5;
        width: 10px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background: #cccccc;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: #bbbbbb;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
"""

THEME_STYLES = {"dark": DARK_STYLESHEET, "light": LIGHT_STYLESHEET}


def apply_theme(widget: QMainWindow, theme: str) -> None:
    widget.setStyleSheet(THEME_STYLES.get(theme, DARK_STYLESHEET))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} – PHP QA Toolbox")
        self.resize(1024, 768)
        self.theme = "dark"

        # Widgets populated by SettingsTab and LogsTab
        self.project_combo: QComboBox | None = None
        self.project_name_edit: QLineEdit | None = None
        self.framework_combo: QComboBox | None = None
        self.php_path_edit: QLineEdit | None = None
        self.php_service_edit: QLineEdit | None = None
        self.server_port_edit: QSpinBox | None = None
        self.docker_checkbox: QCheckBox | None = None
        self.yii_template_combo: QComboBox | None = None
        self.log_path_edit: QLineEdit | None = None
        self.remote_combo: QComboBox | None = None
        self.compose_files_edit: QLineEdit | None = None
        self.compose_profile_edit: QLineEdit | None = None
        self.refresh_spin: QSpinBox | None = None
        self.theme_combo: QComboBox | None = None
        self.terminal_checkbox: QCheckBox | None = None
        self.log_view: QTextEdit | None = None

        self.tabs = QTabWidget()
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.help_button = QPushButton("")
        self.help_button.setIcon(get_icon("help-about"))
        self.help_button.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.help_button)
        main_layout.addLayout(header_layout)

        main_layout.addWidget(self.tabs)

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setMinimumHeight(100)
        self.output_view.setMaximumHeight(180)
        main_layout.addWidget(self.output_view)

        self.clear_output_button = QPushButton("Clear Output")
        self.clear_output_button.setIcon(get_icon("edit-clear"))
        self.clear_output_button.clicked.connect(self.clear_output)
        main_layout.addWidget(self.clear_output_button)

        self.setCentralWidget(central_widget)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.server_process = None
        self.project_running = False
        self.settings_dirty = False

        # Redirect stdout to the output view only
        self._stdout_logger = QTextEditLogger(
            self.output_view,
            sys.stdout,
            echo=False,
        )
        sys.stdout = self._stdout_logger

        # Directory containing project files and PHP executable path
        self.project_path = ""
        # list of dicts with at least ``path`` and ``name`` keys
        self.projects: list[dict] = []
        self.framework_choice = "Laravel"
        self.php_path = "php"
        self.php_service = "php"
        self.server_port = 8000
        self.use_docker = False
        self.compose_files: list[str] = []
        self.compose_profile = ""
        self.yii_template = "basic"
        self.log_paths: list[str] = []
        self.git_remote = ""
        self.max_log_lines = DEFAULT_MAX_LOG_LINES
        self.enable_terminal = False
        self.auto_refresh_secs = 5
        self.load_config()
        apply_theme(self, self.theme)

        # initialize tabs
        self.project_tab = ProjectTab(self)
        self.tabs.addTab(self.project_tab, "Project")

        self.git_tab = GitTab(self)
        self.git_index = self.tabs.addTab(self.git_tab, "Git")

        self.database_tab = DatabaseTab(self)
        self.tabs.addTab(self.database_tab, "Database")

        self.laravel_tab = LaravelTab(self)
        self.laravel_index = self.tabs.addTab(self.laravel_tab, "Laravel")

        self.symfony_tab = SymfonyTab(self)
        self.symfony_index = self.tabs.addTab(self.symfony_tab, "Symfony")

        self.yii_tab = YiiTab(self)
        self.yii_index = self.tabs.addTab(self.yii_tab, "Yii")

        self.docker_tab = DockerTab(self)
        self.docker_index = self.tabs.addTab(self.docker_tab, "Docker")

        self.logs_tab = LogsTab(self)
        self.tabs.addTab(self.logs_tab, "Logs")

        self.terminal_tab = TerminalTab(self)
        self.terminal_index = self.tabs.addTab(self.terminal_tab, "Terminal")

        self.settings_tab = SettingsTab(self)
        self.settings_index = self.tabs.addTab(self.settings_tab, "Settings")
        self.update_settings_tab_title()

        # docker tab availability
        self.tabs.setTabVisible(self.docker_index, self.use_docker)
        self.tabs.setTabEnabled(self.docker_index, self.use_docker)

        # laravel tab availability
        show_fw = self.framework_choice == "Laravel"
        self.tabs.setTabVisible(self.laravel_index, show_fw)
        self.tabs.setTabEnabled(self.laravel_index, show_fw)

        show_symfony = self.framework_choice == "Symfony"
        self.tabs.setTabVisible(self.symfony_index, show_symfony)
        self.tabs.setTabEnabled(self.symfony_index, show_symfony)

        show_yii = self.framework_choice == "Yii"
        self.tabs.setTabVisible(self.yii_index, show_yii)
        self.tabs.setTabEnabled(self.yii_index, show_yii)

        # terminal tab availability
        self.tabs.setTabVisible(self.terminal_index, self.enable_terminal)
        self.tabs.setTabEnabled(self.terminal_index, self.enable_terminal)

        # populate settings widgets with loaded values
        if self.project_combo is not None:
            self.project_combo.setCurrentText(self.project_path)
        if (
            self.framework_combo is not None
            and self.framework_choice
            in [
                self.framework_combo.itemText(i)
                for i in range(self.framework_combo.count())
            ]
        ):
            self.framework_combo.setCurrentText(self.framework_choice)

        if self.project_path:
            self.git_tab.load_branches()
        else:
            if not self.projects:
                QTimer.singleShot(0, self.show_welcome_dialog)
            else:
                QTimer.singleShot(0, self.choose_project)

        if (
            hasattr(self, "_geom_size")
            and isinstance(self._geom_size, list)
            and len(self._geom_size) == 2
            and all(isinstance(i, int) for i in self._geom_size)
        ):
            self.resize(*self._geom_size)

        if (
            hasattr(self, "_geom_pos")
            and isinstance(self._geom_pos, list)
            and len(self._geom_pos) == 2
            and all(isinstance(i, int) for i in self._geom_pos)
        ):
            self.move(*self._geom_pos)

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.update_run_buttons()

    def load_config(self):
        data = load_config()
        self.projects = []
        for entry in data.get("projects", []):
            if isinstance(entry, dict) and "path" in entry:
                name = entry.get("name", Path(entry["path"]).name)
                proj = {"path": entry["path"], "name": name}
                for k, v in entry.items():
                    if k not in proj:
                        proj[k] = v
                self.projects.append(proj)
            elif isinstance(entry, str):
                self.projects.append({"path": entry, "name": Path(entry).name})
        self.project_path = data.get("current_project", self.project_path)
        if not self.projects and data.get("project_path"):
            path = data["project_path"]
            self.projects = [{"path": path, "name": Path(path).name}]
        if not self.project_path and self.projects:
            self.project_path = self.projects[0]["path"]

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
        self.log_paths = settings.get("log_paths")
        if not self.log_paths:
            legacy = settings.get("log_path", data.get("log_path"))
            if legacy:
                self.log_paths = [legacy]
            else:
                self.log_paths = self.default_log_paths(self.framework_choice)
        self.git_remote = settings.get(
            "git_remote", data.get("git_remote", self.git_remote)
        )
        self.compose_files = settings.get(
            "compose_files", data.get("compose_files", self.compose_files)
        )
        self.compose_profile = settings.get(
            "compose_profile", data.get("compose_profile", self.compose_profile)
        )
        self.auto_refresh_secs = settings.get(
            "auto_refresh_secs",
            data.get("auto_refresh_secs", self.auto_refresh_secs),
        )
        self.enable_terminal = settings.get(
            "enable_terminal",
            data.get("enable_terminal", self.enable_terminal),
        )

        self.theme = data.get("theme", self.theme)

        self.max_log_lines = settings.get(
            "max_log_lines",
            data.get("max_log_lines", self.max_log_lines),
        )

        self._geom_size = data.get("window_size")
        self._geom_pos = data.get("window_position")

    def _compose_prefix(self) -> list[str]:
        prefix = ["docker", "compose"]
        for f in self.compose_files:
            prefix.extend(["-f", f])
        if self.compose_profile:
            prefix.extend(["--profile", self.compose_profile])
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

    def update_run_buttons(self) -> None:
        """Enable or disable start and stop buttons based on running state."""
        if hasattr(self, "project_tab"):
            if hasattr(self.project_tab, "start_btn"):
                self.project_tab.start_btn.setEnabled(not self.project_running)
            if hasattr(self.project_tab, "stop_btn"):
                self.project_tab.stop_btn.setEnabled(self.project_running)

    def apply_project_settings(self) -> None:
        """Load settings for the current project and update widgets."""
        data = load_config()
        settings = DEFAULT_PROJECT_SETTINGS.copy()
        settings.update(data.get("project_settings", {}).get(self.project_path, {}))

        self.framework_choice = cast(str, settings["framework"])
        self.php_path = cast(str, settings["php_path"])
        self.php_service = cast(str, settings["php_service"])
        self.server_port = int(cast(Any, settings["server_port"]))
        self.use_docker = bool(settings["use_docker"])
        self.yii_template = cast(str, settings["yii_template"])
        value = settings.get("log_paths")
        self.log_paths = list(cast(list[str], value)) if isinstance(value, list) else []
        if not self.log_paths:
            legacy = settings.get("log_path")
            if legacy:
                self.log_paths = [cast(str, legacy)]
            else:
                self.log_paths = self.default_log_paths(self.framework_choice)
        self.git_remote = cast(str, settings["git_remote"])
        comps = settings.get("compose_files")
        self.compose_files = (
            list(cast(list[str], comps)) if isinstance(comps, list) else []
        )
        self.compose_profile = cast(str, settings.get("compose_profile", ""))
        self.auto_refresh_secs = int(cast(Any, settings["auto_refresh_secs"]))
        self.max_log_lines = int(
            cast(Any, settings.get("max_log_lines", self.max_log_lines))
        )
        self.enable_terminal = bool(
            settings.get("enable_terminal", self.enable_terminal)
        )

        if self.framework_combo is not None:
            self.framework_combo.setCurrentText(self.framework_choice)
        if self.php_path_edit is not None:
            self.php_path_edit.setText(self.php_path)
        if self.php_service_edit is not None:
            self.php_service_edit.setText(self.php_service)
        if self.server_port_edit is not None:
            self.server_port_edit.setValue(self.server_port)
        if self.docker_checkbox is not None:
            self.docker_checkbox.setChecked(self.use_docker)
        if self.yii_template_combo is not None:
            self.yii_template_combo.setCurrentText(self.yii_template)
        if self.settings_tab is not None and hasattr(
            self.settings_tab, "set_log_paths"
        ):
            self.settings_tab.set_log_paths(self.log_paths)
        if self.remote_combo is not None:
            remotes = self.git_tab.get_remotes() if hasattr(self, "git_tab") else []
            if self.git_remote and self.git_remote not in remotes:
                self.remote_combo.addItem(self.git_remote)
            self.remote_combo.setCurrentText(self.git_remote)
        if (
            hasattr(self, "settings_tab")
            and hasattr(self.settings_tab, "set_compose_files")
        ):
            self.settings_tab.set_compose_files(self.compose_files)
        elif self.compose_files_edit is not None:
            self.compose_files_edit.setText(";".join(self.compose_files))
        if self.compose_profile_edit is not None:
            self.compose_profile_edit.setText(self.compose_profile)
        if self.refresh_spin is not None:
            self.refresh_spin.setValue(self.auto_refresh_secs)
        if self.terminal_checkbox is not None:
            self.terminal_checkbox.setChecked(self.enable_terminal)
        if hasattr(self, "logs_tab"):
            self.logs_tab.update_timer_interval(self.auto_refresh_secs)
        if hasattr(self, "terminal_index"):
            self.tabs.setTabVisible(self.terminal_index, self.enable_terminal)
            self.tabs.setTabEnabled(self.terminal_index, self.enable_terminal)

        self.mark_settings_saved()

        if (
            hasattr(self, "project_tab")
            and hasattr(self.project_tab, "update_php_tools")
        ):
            self.project_tab.update_php_tools()

    def run_command(self, command: list[str]) -> None:
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
                result = subprocess.run(
                    command, capture_output=True, text=True, cwd=cwd
                )
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(result.stderr.strip())
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")

        print(f"$ {' '.join(command)}")
        self.executor.submit(task)

    def ensure_project_path(self) -> bool:
        if not self.project_path:
            print("Project path not set")
            self.show_welcome_dialog(exit_if_none=False)
            return False
        return True

    def set_current_project(self, path: str) -> None:
        if not path:
            return
        self.project_path = path
        if self.log_view is not None:
            self.log_view.setPlainText("")
        proj = next((p for p in self.projects if p.get("path") == path), None)
        if proj is None:
            proj = {"path": path, "name": Path(path).name}
            self.projects.append(proj)
        if self.project_combo is not None:
            self.project_combo.blockSignals(True)
            if path not in [
                self.project_combo.itemData(i)
                for i in range(self.project_combo.count())
            ]:
                self.project_combo.addItem(proj["name"], path)
            index = self.project_combo.findData(path)
            if index >= 0:
                self.project_combo.setItemText(index, proj["name"])
                self.project_combo.setCurrentIndex(index)
            else:
                self.project_combo.setCurrentText(proj["name"])
            self.project_combo.blockSignals(False)
        if self.project_name_edit is not None:
            self.project_name_edit.setText(proj.get("name", Path(path).name))
        if hasattr(self, "git_tab"):
            self.git_tab.load_branches()

        if hasattr(self, "terminal_index"):
            self.tabs.setTabVisible(self.terminal_index, self.enable_terminal)
            self.tabs.setTabEnabled(self.terminal_index, self.enable_terminal)

        self.apply_project_settings()

    def add_project(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Project Path")
        if path:
            self.set_current_project(path)
            self.save_settings()

    def choose_project(self) -> None:
        if not self.projects:
            self.show_welcome_dialog()
            return
        names = [p["name"] for p in self.projects]
        current_index = next(
            (i for i, p in enumerate(self.projects) if p["path"] == self.project_path),
            0,
        )
        name, ok = QInputDialog.getItem(
            self,
            "Choose Project",
            "Select project:",
            names,
            current_index,
            editable=False,
        )
        if ok and name:
            for p in self.projects:
                if p["name"] == name:
                    self.set_current_project(p["path"])
                    break

    def show_welcome_dialog(self, exit_if_none: bool = True) -> None:
        dlg = WelcomeDialog(self)
        dlg.exec()
        if exit_if_none and not self.projects:
            self.close()

    def current_framework(self):
        if self.framework_combo is not None:
            return self.framework_combo.currentText()
        return "None"

    def default_log_paths(
        self,
        framework: str | None = None,
        template: str | None = None,
    ) -> list[str]:
        """Return default log file paths for the given framework."""
        if framework is None:
            framework = self.framework_choice
        if framework == "Laravel":
            return [str(Path("storage") / "logs" / "laravel.log")]
        if framework == "Symfony":
            return [str(Path("var") / "log" / "dev.log")]
        if framework == "Yii":
            tmpl = template if template is not None else self.yii_template
            if tmpl == "advanced":
                return [
                    str(Path(part) / "runtime" / "logs" / "app.log")
                    for part in ["frontend", "backend", "console"]
                ]
            return [str(Path("runtime") / "log" / "app.log")]
        return []

    def _tail_file(self, path: Path, lines: int) -> str:
        """Return the last ``lines`` lines from ``path``."""
        try:
            with open(str(path), "rb") as f:
                f.seek(0, os.SEEK_END)
                remaining = f.tell()
                block_size = 4096
                data = b""
                line_count = 0
                while remaining > 0 and line_count <= lines:
                    read_size = block_size if remaining >= block_size else remaining
                    remaining -= read_size
                    f.seek(remaining)
                    chunk = f.read(read_size)
                    data = chunk + data
                    line_count = data.count(b"\n")
                lines_data = data.splitlines()[-lines:]
                return "\n".join(line.decode("utf-8", "replace") for line in lines_data)
        except OSError as e:
            return f"Failed to read log file: {e}"

    def refresh_logs(self) -> None:
        if not self.ensure_project_path():
            return

        framework = self.current_framework()
        log_contents = ""
        parts: list[str]
        if framework == "Laravel":
            log_files = self.log_paths or self.default_log_paths("Laravel")
            selector = getattr(self.logs_tab, "log_selector", None)
            if selector and selector.currentData():
                log_files = [selector.currentData()]

            parts = []
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                heading = f"=== {file} ===" if len(log_files) > 1 else ""
                parts.append(f"{heading}\n{content}" if heading else content)
            log_contents = "\n\n".join(parts)
        elif framework == "Symfony":
            log_files = self.log_paths or self.default_log_paths("Symfony")

            parts = []
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                heading = f"=== {file} ===" if len(log_files) > 1 else ""
                parts.append(f"{heading}\n{content}" if heading else content)
            log_contents = "\n\n".join(parts)
        elif framework == "Yii":
            log_files = self.log_paths or self.default_log_paths("Yii")

            parts = []
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                heading = f"=== {file} ===" if len(log_files) > 1 else ""
                parts.append(f"{heading}\n{content}" if heading else content)
            log_contents = "\n\n".join(parts)
        else:
            log_contents = f"Logs not implemented for {framework}"

        if self.log_view is not None:
            self.log_view.setPlainText(log_contents.strip())

    def save_settings(self) -> None:
        if self.project_combo is not None:
            project_path = self.project_combo.currentData()
            if not project_path:
                project_path = self.project_combo.currentText()
        else:
            project_path = self.project_path
        assert self.framework_combo is not None
        framework = self.framework_combo.currentText()
        assert self.php_path_edit is not None
        php_path = self.php_path_edit.text()
        php_service = (
            self.php_service_edit.text()
            if self.php_service_edit is not None
            else self.php_service
        )
        server_port = (
            self.server_port_edit.value()
            if self.server_port_edit is not None
            else self.server_port
        )
        assert self.docker_checkbox is not None
        use_docker = self.docker_checkbox.isChecked()
        yii_template = (
            self.yii_template_combo.currentText()
            if self.yii_template_combo is not None
            else self.yii_template
        )
        if self.settings_tab is not None and hasattr(
            self.settings_tab, "log_path_edits"
        ):
            paths = [e.text() for e in self.settings_tab.log_path_edits if e.text()]
        else:
            paths = list(self.log_paths)
        git_remote = (
            self.remote_combo.currentText()
            if self.remote_combo is not None
            else self.git_remote
        )
        if (
            self.settings_tab is not None
            and hasattr(self.settings_tab, "compose_file_edits")
        ):
            compose_files = [
                e.text().strip()
                for e in self.settings_tab.compose_file_edits
                if e.text().strip()
            ]
        else:
            compose_text = (
                self.compose_files_edit.text()
                if self.compose_files_edit is not None
                else ";".join(self.compose_files)
            )
            compose_files = [p.strip() for p in compose_text.split(";") if p.strip()]
        compose_profile = (
            self.compose_profile_edit.text()
            if self.compose_profile_edit is not None
            else self.compose_profile
        )
        auto_refresh_secs = (
            self.refresh_spin.value()
            if self.refresh_spin is not None
            else self.auto_refresh_secs
        )
        theme = (
            self.theme_combo.currentText().lower()
            if self.theme_combo is not None
            else self.theme
        )
        enable_terminal = (
            self.terminal_checkbox.isChecked()
            if self.terminal_checkbox is not None
            else self.enable_terminal
        )

        if (
            not project_path
            or (not php_path and not use_docker)
            or (use_docker and not php_service)
            or server_port <= 0
        ):
            QMessageBox.warning(
                self, "Invalid settings", "All settings fields must be filled out."
            )
            return

        if not os.path.isdir(project_path):
            QMessageBox.warning(
                self,
                "Invalid project path",
                "The specified project path does not exist.",
            )
            print(f"Failed to save settings: directory does not exist - {project_path}")
            return

        if not use_docker:
            valid_path = os.path.isfile(php_path)
            if not valid_path:
                valid_path = shutil.which(php_path) is not None
            if not valid_path:
                QMessageBox.warning(
                    self,
                    "Invalid PHP path",
                    "The specified PHP executable was not found.",
                )
                print(f"Failed to save settings: php not found - {php_path}")
                return

        self.project_path = project_path
        project_name = Path(project_path).name
        if self.project_name_edit is not None:
            text = self.project_name_edit.text().strip()
            if text:
                project_name = text
        existing = next(
            (p for p in self.projects if p.get("path") == project_path), None
        )
        if existing:
            existing["name"] = project_name
        else:
            self.projects.append({"path": project_path, "name": project_name})
        if self.project_combo is not None:
            idx = self.project_combo.findData(project_path)
            if idx >= 0:
                self.project_combo.setItemText(idx, project_name)
            else:
                self.project_combo.addItem(project_name, project_path)
        self.framework_choice = framework
        self.php_path = php_path
        self.php_service = php_service or self.php_service
        self.server_port = server_port
        self.use_docker = use_docker
        self.yii_template = yii_template
        self.log_paths = paths
        self.git_remote = git_remote
        self.compose_files = compose_files
        self.compose_profile = compose_profile.strip()
        self.auto_refresh_secs = int(auto_refresh_secs)
        self.theme = theme
        self.enable_terminal = enable_terminal
        self.max_log_lines = int(getattr(self, "max_log_lines", DEFAULT_MAX_LOG_LINES))

        data = load_config()
        settings = data.get("project_settings", {})
        settings[project_path] = {
            "framework": framework,
            "php_path": php_path,
            "php_service": php_service,
            "server_port": server_port,
            "use_docker": use_docker,
            "yii_template": yii_template,
            "log_paths": paths,
            "git_remote": git_remote,
            "compose_files": self.compose_files,
            "compose_profile": self.compose_profile,
            "auto_refresh_secs": self.auto_refresh_secs,
            "max_log_lines": self.max_log_lines,
            "enable_terminal": self.enable_terminal,
        }
        data.update(
            {
                "projects": self.projects,
                "current_project": project_path,
                "project_settings": settings,
                "theme": self.theme,
            }
        )
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")

        apply_theme(self, self.theme)
        print("Settings saved!")
        self.mark_settings_saved()

        if hasattr(self, "logs_tab"):
            self.logs_tab.update_timer_interval(self.auto_refresh_secs)
            if hasattr(self.logs_tab, "set_log_paths"):
                self.logs_tab.set_log_paths(self.log_paths)

        if hasattr(self, "git_tab"):
            self.git_tab.load_branches()

    def artisan(self, *args: str) -> None:
        self.ensure_project_path()
        artisan_file = Path(self.project_path) / "artisan"
        self.run_command([self.php_path, str(artisan_file), *args])

    def symfony(self, *args: str) -> None:
        self.ensure_project_path()
        console = Path(self.project_path) / "bin" / "console"
        self.run_command([self.php_path, str(console), *args])

    def yii(self, *args: str) -> None:
        self.ensure_project_path()
        script = os.path.join(self.project_path, "yii")
        yii_bat = os.path.join(self.project_path, "yii.bat")
        if os.name == "nt" and os.path.isfile(yii_bat):
            script = yii_bat
        elif not os.path.isfile(script) and os.path.isfile(script + ".bat"):
            script = script + ".bat"
        self.run_command([self.php_path, script, *args])

    def migrate(self) -> None:
        fw = self.current_framework()
        if fw == "Laravel":
            self.artisan("migrate")
        elif fw == "Symfony":
            self.symfony("doctrine:migrations:migrate")
        elif fw == "Yii":
            self.yii("migrate")
        else:
            print(f"Migrate not implemented for {fw}")

    def rollback(self) -> None:
        fw = self.current_framework()
        if fw == "Laravel":
            self.artisan("migrate:rollback")
        elif fw == "Symfony":
            self.symfony("doctrine:migrations:migrate", "prev")
        elif fw == "Yii":
            self.yii("migrate/down", "1")
        else:
            print(f"Rollback not implemented for {fw}")

    def fresh(self) -> None:
        if self.current_framework() == "Laravel":
            self.artisan("migrate:fresh")
        else:
            print(f"Fresh not implemented for {self.current_framework()}")

    def seed(self) -> None:
        if self.current_framework() == "Laravel":
            self.artisan("db:seed")
        else:
            print(f"Seed not implemented for {self.current_framework()}")

    def phpunit(self) -> None:
        self.ensure_project_path()
        phpunit_file = Path(self.project_path) / "vendor" / "bin" / "phpunit"
        self.run_command([self.php_path, str(phpunit_file)])

    def start_project(self) -> None:
        if self.project_running:
            print("Project already running")
            return

        if self.use_docker:
            self.run_command(["docker", "compose", "up", "-d"])
            self.project_running = True
            self.update_run_buttons()
            return

        if self.server_process and self.server_process.poll() is None:
            print("Project already running")
            return

        if not self.ensure_project_path():
            return

        if self.current_framework() == "Laravel":
            artisan_file = Path(self.project_path) / "artisan"
            command = [self.php_path, str(artisan_file), "serve"]
        else:
            # fallback generic PHP server
            command = [
                self.php_path,
                "-S",
                f"localhost:{self.server_port}",
                "-t",
                self.project_path,  # os.path.join(self.project_path, "public")
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
                popen_args["creationflags"] = getattr(
                    subprocess, "CREATE_NEW_PROCESS_GROUP", 0
                )
            else:
                popen_args["start_new_session"] = True

            self.server_process = subprocess.Popen(
                command, **cast(dict[str, Any], popen_args)
            )

            def stream():
                assert self.server_process is not None
                for line in self.server_process.stdout:
                    print(line.rstrip())

            self.executor.submit(stream)
            self.project_running = True
            self.update_run_buttons()
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")

    def stop_project(self) -> None:
        if self.use_docker:
            self.run_command(["docker", "compose", "down"])
            self.project_running = False
            self.update_run_buttons()
            return

        if not self.project_running:
            print("Project is not running")
            return

        if self.server_process and self.server_process.poll() is None:
            print("Stopping project...")
            try:
                if os.name == "nt":
                    if hasattr(self.server_process, "send_signal"):
                        self.server_process.send_signal(
                            getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM)
                        )
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
        self.project_running = False
        self.update_run_buttons()

    def closeEvent(self, event: "QCloseEvent | None") -> None:
        if self.server_process and self.server_process.poll() is None:
            try:
                if os.name == "nt":
                    if hasattr(self.server_process, "send_signal"):
                        self.server_process.send_signal(
                            getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM)
                        )
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
        # Restore original stdout before shutting down
        sys.stdout = self._stdout_logger.original_stdout
        data = load_config()
        data["window_size"] = [self.width(), self.height()]
        data["window_position"] = [self.x(), self.y()]
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")
        super().closeEvent(event)

    def show_about_dialog(self) -> None:
        from .about_dialog import AboutDialog

        dlg = AboutDialog(self)
        dlg.exec()

    def on_tab_changed(self, index: int) -> None:
        if index == getattr(self, "git_index", -1):
            self.git_tab.load_branches()

    def clear_output(self) -> None:
        self.output_view.clear()

    def clear_log_file(self) -> None:
        """Truncate the configured log file if it exists."""
        log_file = self.log_paths[0] if self.log_paths else ""
        if hasattr(self, "logs_tab") and hasattr(self.logs_tab, "log_selector"):
            sel = self.logs_tab.log_selector.currentData()
            if sel:
                log_file = sel
        if not log_file:
            self.refresh_logs()
            return
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = Path(self.project_path) / log_path

        if not log_path.exists():
            self.refresh_logs()
            return

        reply = QMessageBox.question(
            self,
            "Clear Log",
            "Are you sure you want to clear the log file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(str(log_path), "w", encoding="utf-8"):
                    pass
            except OSError as e:
                print(f"Failed to clear log file: {e}")

        self.refresh_logs()
