import sys
import os
from pathlib import Path
import subprocess
import signal
import concurrent.futures
import builtins
import shutil
import webbrowser
import socket
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    QSystemTrayIcon,
    QMenu,
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QShortcut, QKeySequence, QAction
from typing import TYPE_CHECKING, Any, Callable, cast
from .utils import expand_log_paths, is_git_repo

if TYPE_CHECKING:
    from PyQt6.QtWidgets import (
        QComboBox,
        QLineEdit,
        QSpinBox,
        QCheckBox,
    )
    from PyQt6.QtGui import QCloseEvent
from . import APP_NAME

from .config import (
    load_config,
    save_config,
    DEFAULT_PROJECT_SETTINGS,
    DEFAULT_MAX_LOG_LINES,
)
from .qtextedit_logger import QTextEditLogger
from .welcome_dialog import WelcomeDialog
from .ui import create_button

from .tabs.project_tab import ProjectTab
from .tabs.git_tab import GitTab
from .tabs.database_tab import DatabaseTab
from .tabs.laravel_tab import LaravelTab
from .tabs.symfony_tab import SymfonyTab
from .tabs.yii_tab import YiiTab
from .tabs.node_tab import NodeTab
from .tabs.composer_tab import ComposerTab
from .tabs.makefile_tab import MakefileTab
from .tabs.docker_tab import DockerTab
from .tabs.logs_tab import LogsTab
from .tabs.terminal_tab import TerminalTab
from .tabs.env_tab import EnvTab
from .tabs.settings_tab import SettingsTab
from .tabs.about_tab import AboutTab

# allow tests to monkeypatch file operations easily
open = builtins.open


def _port_in_use(port: int) -> bool:
    """Return True if ``port`` is already bound on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
        except OSError:
            return True
    return False


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


def get_system_theme() -> str:
    """Return the operating system color scheme as ``dark`` or ``light``."""
    app = QApplication.instance()
    if app is None:
        return "dark"
    hints = cast(QApplication, app).styleHints()
    if hints is None:
        return "dark"
    scheme = hints.colorScheme()
    if scheme == Qt.ColorScheme.Dark:
        return "dark"
    if scheme == Qt.ColorScheme.Light:
        return "light"
    return "dark"


def apply_theme(widget: QMainWindow, theme: str) -> None:
    widget.setStyleSheet(THEME_STYLES.get(theme, DARK_STYLESHEET))


class MainWindow(QMainWindow):
    notify_signal = pyqtSignal(str, str)
    call_later = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.notify_signal.connect(self._show_notification)
        self.call_later.connect(lambda f: f())
        self.setWindowTitle(f"{APP_NAME} – PHP QA Toolbox")
        self.resize(1024, 768)
        self.setMinimumSize(425, 300)
        self.theme_choice = "dark"
        self.os_theme = get_system_theme()
        self.follow_system_theme = False
        self.theme = "dark"

        # Widgets populated by SettingsTab and LogsTab
        self.project_combo: QComboBox | None = None
        self.framework_combo: QComboBox | None = None
        self.php_path_edit: QLineEdit | None = None
        self.php_service_edit: QLineEdit | None = None
        self.db_service_edit: QLineEdit | None = None
        self.server_port_edit: QSpinBox | None = None
        self.docker_project_path_edit: QLineEdit | None = None
        self.docker_checkbox: QCheckBox | None = None
        self.yii_template_combo: QComboBox | None = None
        self.log_dir_edit: QLineEdit | None = None
        self.remote_combo: QComboBox | None = None
        self.compose_files_edit: QLineEdit | None = None
        self.compose_profile_edit: QLineEdit | None = None
        self.refresh_spin: QSpinBox | None = None
        self.theme_combo: QComboBox | None = None
        self.terminal_checkbox: QCheckBox | None = None
        self.open_browser_checkbox: QCheckBox | None = None
        self.console_output_checkbox: QCheckBox | None = None
        self.log_view: QTextEdit | None = None

        self.tabs = QTabWidget()
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self.tabs)

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setFixedHeight(200)
        main_layout.addWidget(self.output_view)

        self.clear_output_button = create_button("Clear Output", "edit-clear")
        self.clear_output_button.clicked.connect(self.clear_output)
        main_layout.addWidget(self.clear_output_button)

        self.setCentralWidget(central_widget)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.server_process = None
        self.project_running = False
        self.settings_dirty = False
        self._tray_icon: QSystemTrayIcon | None = None
        self._tray_menu: QMenu | None = None
        self._tray_show_action: QAction | None = None
        self._tray_start_action: QAction | None = None
        self.tray_enabled = False
        self.tray_checkbox: QCheckBox | None = None

        # Global shortcut to save settings
        self._save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self._save_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self._save_shortcut.activated.connect(self.save_settings)

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
        self.db_service = "db"
        self.docker_project_path = "/app"
        self.server_port = 8000
        self.use_docker = False
        self.compose_files: list[str] = []
        self.compose_profile = ""
        self.yii_template = "basic"
        self.log_dirs: list[str] = []
        self.git_remote = ""
        self.is_git_repo = False
        self.max_log_lines = DEFAULT_MAX_LOG_LINES
        self.enable_terminal = False
        self.auto_refresh_secs = 5
        self.open_browser = False
        self.show_console_output = False
        self.load_config()
        self.use_node = self.project_uses_node(self.project_path)
        self.use_composer = self.project_uses_composer(self.project_path)
        self.has_makefile = self.project_has_makefile(self.project_path)
        if self.follow_system_theme:
            apply_theme(self, self.os_theme)
            self.theme = self.os_theme
        else:
            apply_theme(self, self.theme_choice)
            self.theme = self.theme_choice

        app = QApplication.instance()
        if app is not None:
            hints = cast(QApplication, app).styleHints()
            if hints is not None:
                hints.colorSchemeChanged.connect(self._on_system_theme_changed)

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

        self.node_tab = NodeTab(self)
        self.node_index = self.tabs.addTab(self.node_tab, "Node")
        self.tabs.setTabVisible(self.node_index, self.use_node)
        self.tabs.setTabEnabled(self.node_index, self.use_node)

        self.composer_tab = ComposerTab(self)
        self.composer_index = self.tabs.addTab(self.composer_tab, "Composer")
        self.tabs.setTabVisible(self.composer_index, self.use_composer)
        self.tabs.setTabEnabled(self.composer_index, self.use_composer)

        self.make_tab = MakefileTab(self)
        self.make_index = self.tabs.addTab(self.make_tab, "Make")
        self.tabs.setTabVisible(self.make_index, self.has_makefile)
        self.tabs.setTabEnabled(self.make_index, self.has_makefile)

        self.logs_tab = LogsTab(self)
        self.logs_index = self.tabs.addTab(self.logs_tab, "Logs")

        self.env_tab = EnvTab(self)
        self.env_index = self.tabs.addTab(self.env_tab, "Env")

        self.terminal_tab = TerminalTab(self)
        self.terminal_index = self.tabs.addTab(self.terminal_tab, "Terminal")

        self.about_tab = AboutTab(self)
        self.about_index = self.tabs.addTab(self.about_tab, "About")

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

        log_visible = self.framework_choice in ["Laravel", "Symfony", "Yii"]
        self.tabs.setTabVisible(self.logs_index, log_visible)
        self.tabs.setTabEnabled(self.logs_index, log_visible)

        # env tab visibility based on project selection
        show_env = bool(self.project_path)
        self.tabs.setTabVisible(self.env_index, show_env)
        self.tabs.setTabEnabled(self.env_index, show_env)

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
            if self.is_git_repo:
                self.git_tab.load_branches()
            if hasattr(self.git_tab, "update_visibility"):
                self.git_tab.update_visibility()
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
        self._update_responsive_layout()
        self.update_window_title()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_layout()

    def showEvent(self, event):
        super().showEvent(event)
        if self.tray_enabled:
            self._init_tray_icon()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.tray_enabled:
            self._update_tray_menu()

    def load_config(self):
        data = load_config()
        self.projects = []
        for entry in data.get("projects", []):
            if isinstance(entry, dict) and "path" in entry:
                name = entry.get("name", Path(entry["path"]).name)
                proj_dict = {"path": entry["path"], "name": name}
                for k, v in entry.items():
                    if k not in proj_dict:
                        proj_dict[k] = v
                self.projects.append(proj_dict)
            elif isinstance(entry, str):
                self.projects.append({"path": entry, "name": Path(entry).name})
        self.project_path = data.get("current_project", self.project_path)
        if not self.project_path and self.projects:
            self.project_path = self.projects[0]["path"]
        self.is_git_repo = bool(self.project_path) and is_git_repo(self.project_path)

        proj: dict[str, Any] | None = next(
            (p for p in data.get("projects", []) if p.get("path") == self.project_path),
            None,
        )
        settings: dict[str, Any] = DEFAULT_PROJECT_SETTINGS.copy()
        settings["framework"] = self.framework_choice
        settings.update(data.get("project_settings", {}).get(self.project_path, {}))
        if isinstance(proj, dict):
            temp = proj.copy()
            temp.pop("path", None)
            temp.pop("name", None)
            settings.update(temp)

        self.framework_choice = cast(
            str,
            settings.get("framework", data.get("framework", self.framework_choice)),
        )
        self.php_path = cast(str, settings.get("php_path", data.get("php_path", self.php_path)))
        self.php_service = cast(
            str,
            settings.get("php_service", data.get("php_service", self.php_service)),
        )
        self.db_service = cast(
            str,
            settings.get("db_service", data.get("db_service", self.db_service)),
        )
        self.docker_project_path = cast(
            str,
            settings.get(
                "docker_project_path",
                data.get("docker_project_path", self.docker_project_path),
            ),
        )
        self.server_port = int(
            cast(Any, settings.get("server_port", data.get("server_port", self.server_port)))
        )
        self.use_docker = bool(
            settings.get("use_docker", data.get("use_docker", self.use_docker))
        )
        self.yii_template = cast(
            str,
            settings.get("yii_template", data.get("yii_template", self.yii_template)),
        )
        self.log_dirs = cast(
            list[str], settings.get("log_dirs")
        ) if isinstance(settings.get("log_dirs"), list) else []
        if not self.log_dirs:
            self.log_dirs = self.default_log_dirs(self.framework_choice)
        self.git_remote = cast(
            str,
            settings.get("git_remote", data.get("git_remote", self.git_remote)),
        )
        self.compose_files = (
            list(cast(list[str], settings.get("compose_files")))
            if isinstance(settings.get("compose_files"), list)
            else cast(list[str], data.get("compose_files", self.compose_files))
        )
        self.compose_profile = cast(
            str,
            settings.get("compose_profile", data.get("compose_profile", self.compose_profile)),
        )
        self.auto_refresh_secs = int(
            cast(
                Any,
                settings.get(
                    "auto_refresh_secs",
                    data.get("auto_refresh_secs", self.auto_refresh_secs),
                ),
            )
        )
        self.enable_terminal = bool(
            settings.get("enable_terminal", data.get("enable_terminal", self.enable_terminal))
        )
        self.open_browser = bool(
            settings.get("open_browser", data.get("open_browser", self.open_browser))
        )
        self.show_console_output = bool(
            data.get("show_console_output", self.show_console_output)
        )
        self.tray_enabled = bool(data.get("enable_tray", self.tray_enabled))

        self.theme_choice = data.get("theme", self.theme_choice)
        self.follow_system_theme = self.theme_choice == "system"
        self.theme = self.os_theme if self.follow_system_theme else self.theme_choice

        self.max_log_lines = int(
            cast(
                Any,
                settings.get("max_log_lines", data.get("max_log_lines", self.max_log_lines)),
            )
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

    def on_theme_combo_changed(self, text: str) -> None:
        self.theme_choice = text.lower()
        self.follow_system_theme = self.theme_choice == "system"
        if self.follow_system_theme:
            apply_theme(self, self.os_theme)
            self.theme = self.os_theme
        else:
            apply_theme(self, self.theme_choice)
            self.theme = self.theme_choice
        self.mark_settings_dirty()

    def mark_settings_saved(self):
        if self.settings_dirty:
            self.settings_dirty = False
            self.update_settings_tab_title()

    def notify(self, message: str, title: str = APP_NAME) -> None:
        """Emit a signal to show a transient system notification."""
        self.notify_signal.emit(message, title)

    def _show_notification(self, message: str, title: str = APP_NAME) -> None:
        icon = self._tray_icon
        if icon is None:
            tray_icon = self.windowIcon()
            if tray_icon.isNull():
                from .icons import get_notification_icon

                tray_icon = get_notification_icon()
            icon = QSystemTrayIcon(tray_icon, self)
            self._tray_icon = icon

        icon.show()
        icon.showMessage(title, message)
        if not self.tray_enabled:
            QTimer.singleShot(100, icon.hide)

    def update_run_buttons(self) -> None:
        """Enable or disable start and stop buttons based on running state."""
        if hasattr(self, "project_tab"):
            if hasattr(self.project_tab, "start_btn"):
                self.project_tab.start_btn.setEnabled(not self.project_running)
            if hasattr(self.project_tab, "stop_btn"):
                self.project_tab.stop_btn.setEnabled(self.project_running)

    def update_window_title(self) -> None:
        status = "Running" if self.project_running else "Stopped"
        self.setWindowTitle(f"{APP_NAME} – PHP QA Toolbox – {status}")

    def _update_responsive_layout(self) -> None:
        """Adjust UI elements based on the current window size."""
        width = self.width()

        show_output = width >= 700 and self.show_console_output
        self.output_view.setVisible(show_output)
        self.clear_output_button.setVisible(show_output)

        if hasattr(self, "logs_tab") and hasattr(
            self.logs_tab, "update_responsive_layout"
        ):
            self.logs_tab.update_responsive_layout(width)

        if hasattr(self, "git_tab") and hasattr(
            self.git_tab, "update_responsive_layout"
        ):
            self.git_tab.update_responsive_layout(width)

    def _on_system_theme_changed(self, scheme: Qt.ColorScheme) -> None:
        self.os_theme = "dark" if scheme == Qt.ColorScheme.Dark else "light"
        if self.follow_system_theme:
            apply_theme(self, self.os_theme)
            self.theme = self.os_theme
            if self.theme_combo is not None:
                self.theme_combo.setCurrentText(self.os_theme.capitalize())

    # ------------------------------------------------------------------
    # System tray icon helpers
    # ------------------------------------------------------------------

    def _init_tray_icon(self) -> None:
        if self._tray_icon is None:
            tray_icon = self.windowIcon()
            if tray_icon.isNull():
                from .icons import get_notification_icon

                tray_icon = get_notification_icon()
            icon = QSystemTrayIcon(tray_icon, self)
            menu = QMenu()
            show_action = cast(QAction, menu.addAction("Hide"))
            show_action.triggered.connect(self.toggle_window_visibility)
            start_action = cast(QAction, menu.addAction("Start Project"))
            start_action.triggered.connect(self._on_tray_start_stop)
            quit_action = cast(QAction, menu.addAction("Quit"))
            quit_action.triggered.connect(self._on_tray_quit)
            icon.setContextMenu(menu)
            self._tray_icon = icon
            self._tray_menu = menu
            self._tray_show_action = show_action
            self._tray_start_action = start_action
        self._update_tray_menu()
        self._tray_icon.show()

    def _update_tray_menu(self) -> None:
        if not self._tray_icon or not self._tray_menu:
            return
        if self._tray_show_action:
            text = "Hide" if self.isVisible() else "Show"
            self._tray_show_action.setText(text)
        if self._tray_start_action:
            text = "Stop Project" if self.project_running else "Start Project"
            self._tray_start_action.setText(text)

    def _on_tray_start_stop(self) -> None:
        if self.project_running:
            self.stop_project()
        else:
            self.start_project()
        self._update_tray_menu()

    def _on_tray_quit(self) -> None:
        """Handle tray Quit action by disabling the tray and closing."""
        if self.tray_checkbox is not None:
            self.tray_checkbox.setChecked(False)
        self.tray_enabled = False
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def toggle_window_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
        self._update_tray_menu()

    def apply_project_settings(self) -> None:
        """Load settings for the current project and update widgets."""
        data = load_config()
        self.is_git_repo = bool(self.project_path) and is_git_repo(self.project_path)
        proj = next((p for p in data.get("projects", []) if p.get("path") == self.project_path), None)
        settings = DEFAULT_PROJECT_SETTINGS.copy()
        settings["framework"] = self.framework_choice
        settings.update(data.get("project_settings", {}).get(self.project_path, {}))
        if isinstance(proj, dict):
            temp = proj.copy()
            temp.pop("path", None)
            temp.pop("name", None)
            settings.update(temp)

        self.framework_choice = cast(str, settings["framework"])
        self.php_path = cast(str, settings["php_path"])
        self.php_service = cast(str, settings["php_service"])
        self.db_service = cast(str, settings.get("db_service", "db"))
        self.docker_project_path = cast(str, settings.get("docker_project_path", "/app"))
        self.server_port = int(cast(Any, settings["server_port"]))
        self.use_docker = bool(settings["use_docker"])
        self.yii_template = cast(str, settings["yii_template"])
        value = settings.get("log_dirs")
        self.log_dirs = list(cast(list[str], value)) if isinstance(value, list) else []
        if not self.log_dirs:
            self.log_dirs = self.default_log_dirs(self.framework_choice)
        self.git_remote = cast(str, settings["git_remote"])
        comps = settings.get("compose_files")
        self.compose_files = (
            list(cast(list[str], comps)) if isinstance(comps, list) else []
        )
        self.compose_profile = cast(str, settings.get("compose_profile", ""))
        self.auto_refresh_secs = int(cast(Any, settings["auto_refresh_secs"]))
        self.open_browser = bool(settings.get("open_browser", False))
        self.max_log_lines = int(
            cast(Any, settings.get("max_log_lines", self.max_log_lines))
        )
        self.enable_terminal = bool(settings.get("enable_terminal", self.enable_terminal))
        self.show_console_output = bool(data.get("show_console_output", self.show_console_output))

        if self.framework_combo is not None:
            self.framework_combo.setCurrentText(self.framework_choice)
        if self.php_path_edit is not None:
            self.php_path_edit.setText(self.php_path)
        if self.php_service_edit is not None:
            self.php_service_edit.setText(self.php_service)
        if self.db_service_edit is not None:
            self.db_service_edit.setText(self.db_service)
        if self.server_port_edit is not None:
            self.server_port_edit.setValue(self.server_port)
        if self.docker_checkbox is not None:
            self.docker_checkbox.setChecked(self.use_docker)
        if self.yii_template_combo is not None:
            self.yii_template_combo.setCurrentText(self.yii_template)
        if self.settings_tab is not None and hasattr(
            self.settings_tab, "set_log_dirs"
        ):
            self.settings_tab.set_log_dirs(self.log_dirs)
        if self.remote_combo is not None:
            remotes = self.git_tab.get_remotes() if hasattr(self, "git_tab") else []
            self.remote_combo.clear()
            if remotes:
                self.remote_combo.addItems(remotes)
            if self.git_remote:
                if self.git_remote not in remotes:
                    self.remote_combo.addItem(self.git_remote)
                self.remote_combo.setCurrentText(self.git_remote)
            elif remotes:
                self.remote_combo.setCurrentText(remotes[0])
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
        if self.open_browser_checkbox is not None:
            self.open_browser_checkbox.setChecked(self.open_browser)
        if self.console_output_checkbox is not None:
            self.console_output_checkbox.setChecked(self.show_console_output)
        if hasattr(self, "logs_tab"):
            self.logs_tab.update_timer_interval(self.auto_refresh_secs)
        if hasattr(self, "terminal_index"):
            self.tabs.setTabVisible(self.terminal_index, self.enable_terminal)
            self.tabs.setTabEnabled(self.terminal_index, self.enable_terminal)
        if hasattr(self, "env_index"):
            show_env = bool(self.project_path)
            self.tabs.setTabVisible(self.env_index, show_env)
            self.tabs.setTabEnabled(self.env_index, show_env)
            if show_env and hasattr(self, "env_tab"):
                self.env_tab.load_env()
        if hasattr(self, "node_index"):
            self.use_node = self.project_uses_node()
            self.tabs.setTabVisible(self.node_index, self.use_node)
            self.tabs.setTabEnabled(self.node_index, self.use_node)

        if hasattr(self, "composer_index"):
            self.use_composer = self.project_uses_composer()
            self.tabs.setTabVisible(self.composer_index, self.use_composer)
            self.tabs.setTabEnabled(self.composer_index, self.use_composer)

        self.mark_settings_saved()

        if (
            hasattr(self, "project_tab")
            and hasattr(self.project_tab, "update_php_tools")
        ):
            self.project_tab.update_php_tools()

        if hasattr(self, "node_tab") and hasattr(self.node_tab, "update_npm_scripts"):
            self.node_tab.update_npm_scripts()

        if hasattr(self, "composer_tab") and hasattr(self.composer_tab, "update_composer_scripts"):
            self.composer_tab.update_composer_scripts()

        if hasattr(self, "make_tab") and hasattr(self.make_tab, "update_commands"):
            self.make_tab.update_commands()

    def run_command(
        self,
        command: list[str],
        service: str | None = None,
        callback: Callable[[], None] | None = None,
    ) -> concurrent.futures.Future:
        if self.use_docker:
            if len(command) >= 2 and command[0] == "docker" and command[1] == "compose":
                command = self._compose_prefix() + command[2:]
            else:
                command = self._compose_prefix() + [
                    "exec",
                    "-T",
                    service or self.php_service,
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
                self.notify(f"Finished: {' '.join(command)}")
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")
                self.notify(f"Command not found: {command[0]}")
            finally:
                if callback is not None:
                    # ensure callback runs on the UI thread
                    self.call_later.emit(callback)

        print(f"$ {' '.join(command)}")
        return self.executor.submit(task)

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
        self.is_git_repo = is_git_repo(path)
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
        if hasattr(self, "git_tab"):
            if self.is_git_repo:
                self.git_tab.load_branches()
            if hasattr(self.git_tab, "update_visibility"):
                self.git_tab.update_visibility()
        if hasattr(self, "settings_tab") and hasattr(self.settings_tab, "update_git_visibility"):
            self.settings_tab.update_git_visibility(self.is_git_repo)
        if hasattr(self, "settings_tab") and hasattr(self.settings_tab, "update_git_visibility"):
            self.settings_tab.update_git_visibility(self.is_git_repo)

        if hasattr(self, "terminal_index"):
            self.tabs.setTabVisible(self.terminal_index, self.enable_terminal)
            self.tabs.setTabEnabled(self.terminal_index, self.enable_terminal)
        if hasattr(self, "env_index"):
            self.tabs.setTabVisible(self.env_index, True)
            self.tabs.setTabEnabled(self.env_index, True)
            if hasattr(self, "env_tab"):
                self.env_tab.load_env()
        if hasattr(self, "node_index"):
            self.use_node = self.project_uses_node(path)
            self.tabs.setTabVisible(self.node_index, self.use_node)
            self.tabs.setTabEnabled(self.node_index, self.use_node)

        if hasattr(self, "composer_index"):
            self.use_composer = self.project_uses_composer(path)
            self.tabs.setTabVisible(self.composer_index, self.use_composer)
            self.tabs.setTabEnabled(self.composer_index, self.use_composer)

        if hasattr(self, "make_index"):
            self.has_makefile = self.project_has_makefile(path)
            self.tabs.setTabVisible(self.make_index, self.has_makefile)
            self.tabs.setTabEnabled(self.make_index, self.has_makefile)
            if self.has_makefile and hasattr(self.make_tab, "update_commands"):
                self.make_tab.update_commands()

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

    def default_log_dirs(
        self,
        framework: str | None = None,
        template: str | None = None,
    ) -> list[str]:
        """Return default log directories for the given framework."""
        if framework is None:
            framework = self.framework_choice
        if framework == "Laravel":
            return [str(Path("storage") / "logs")]
        if framework == "Symfony":
            return [str(Path("var") / "log")]
        if framework == "Yii":
            tmpl = template if template is not None else self.yii_template
            if tmpl == "advanced":
                return [
                    str(Path(part) / "runtime" / "logs")
                    for part in ["frontend", "backend", "console"]
                ]
            return [str(Path("runtime") / "log")]
        return []

    def project_uses_node(self, path: str | None = None) -> bool:
        """Return True if the project contains package.json or node_modules."""
        if not (path or self.project_path):
            return False
        base = Path(path or self.project_path)
        return (base / "package.json").is_file() or (base / "node_modules").is_dir()

    def project_uses_composer(self, path: str | None = None) -> bool:
        """Return True if the project contains composer.json or vendor."""
        if not (path or self.project_path):
            return False
        base = Path(path or self.project_path)
        return (base / "composer.json").is_file() or (base / "vendor").is_dir()

    def project_has_makefile(self, path: str | None = None) -> bool:
        """Return True if the project contains a Makefile."""
        if not (path or self.project_path):
            return False
        return Path(path or self.project_path, "Makefile").is_file()

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
            log_files = self.log_dirs or self.default_log_dirs("Laravel")
            selector = getattr(self.logs_tab, "log_selector", None)
            if selector and selector.currentData():
                log_files = [selector.currentData()]
            log_files = expand_log_paths(self.project_path, log_files)

            parts = []
            level_selector = getattr(self.logs_tab, "level_selector", None)
            level = level_selector.currentText() if level_selector else "All"
            level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            allowed = None
            if level != "All" and level in level_order:
                idx = level_order.index(level)
                allowed = set(level_order[idx:])
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                if allowed is not None:
                    content = "\n".join(
                        line
                        for line in content.splitlines()
                        if any(level_marker in line for level_marker in allowed)
                    )
                heading = f"=== {file} ===" if len(log_files) > 1 else ""
                parts.append(f"{heading}\n{content}" if heading else content)
            log_contents = "\n\n".join(parts)
        elif framework == "Symfony":
            log_files = self.log_dirs or self.default_log_dirs("Symfony")
            log_files = expand_log_paths(self.project_path, log_files)

            parts = []
            level_selector = getattr(self.logs_tab, "level_selector", None)
            level = level_selector.currentText() if level_selector else "All"
            level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            allowed = None
            if level != "All" and level in level_order:
                idx = level_order.index(level)
                allowed = set(level_order[idx:])
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                if allowed is not None:
                    content = "\n".join(
                        line
                        for line in content.splitlines()
                        if any(level_marker in line for level_marker in allowed)
                    )
                heading = f"=== {file} ===" if len(log_files) > 1 else ""
                parts.append(f"{heading}\n{content}" if heading else content)
            log_contents = "\n\n".join(parts)
        elif framework == "Yii":
            log_files = self.log_dirs or self.default_log_dirs("Yii")
            log_files = expand_log_paths(self.project_path, log_files)

            parts = []
            level_selector = getattr(self.logs_tab, "level_selector", None)
            level = level_selector.currentText() if level_selector else "All"
            level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            allowed = None
            if level != "All" and level in level_order:
                idx = level_order.index(level)
                allowed = set(level_order[idx:])
            for file in log_files:
                path = Path(file)
                if not path.is_absolute():
                    path = Path(self.project_path) / path
                if path.exists():
                    content = self._tail_file(path, self.max_log_lines)
                else:
                    content = f"Log file not found: {path}"
                if allowed is not None:
                    content = "\n".join(
                        line
                        for line in content.splitlines()
                        if any(level_marker in line for level_marker in allowed)
                    )
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
        db_service = (
            self.db_service_edit.text()
            if self.db_service_edit is not None
            else self.db_service
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
            self.settings_tab, "log_dir_edits"
        ):
            paths = [e.text() for e in self.settings_tab.log_dir_edits if e.text()]
        else:
            paths = list(self.log_dirs)
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
        docker_project_path = (
            self.docker_project_path_edit.text()
            if self.docker_project_path_edit is not None
            else self.docker_project_path
        )
        auto_refresh_secs = (
            self.refresh_spin.value()
            if self.refresh_spin is not None
            else self.auto_refresh_secs
        )
        theme_choice = (
            self.theme_combo.currentText().lower()
            if self.theme_combo is not None
            else self.theme_choice
        )
        enable_terminal = (
            self.terminal_checkbox.isChecked()
            if self.terminal_checkbox is not None
            else self.enable_terminal
        )
        show_console_output = (
            self.console_output_checkbox.isChecked()
            if self.console_output_checkbox is not None
            else self.show_console_output
        )
        open_browser = (
            self.open_browser_checkbox.isChecked()
            if self.open_browser_checkbox is not None
            else self.open_browser
        )
        tray_enabled = (
            self.tray_checkbox.isChecked()
            if self.tray_checkbox is not None
            else self.tray_enabled
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
        self.is_git_repo = is_git_repo(project_path)
        project_name = Path(project_path).name
        if self.project_combo is not None:
            idx = self.project_combo.findData(project_path)
            if idx >= 0:
                text = self.project_combo.itemText(idx).strip()
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
        self.db_service = db_service or self.db_service
        self.server_port = server_port
        self.use_docker = use_docker
        self.yii_template = yii_template
        self.log_dirs = paths
        self.git_remote = git_remote
        self.compose_files = compose_files
        self.compose_profile = compose_profile.strip()
        self.docker_project_path = docker_project_path.strip() or self.docker_project_path
        self.auto_refresh_secs = int(auto_refresh_secs)
        self.theme_choice = theme_choice
        self.follow_system_theme = self.theme_choice == "system"
        if not self.follow_system_theme:
            self.theme = self.theme_choice
        self.enable_terminal = enable_terminal
        self.open_browser = bool(open_browser)
        self.show_console_output = bool(show_console_output)
        self.tray_enabled = bool(tray_enabled)
        self.max_log_lines = int(getattr(self, "max_log_lines", DEFAULT_MAX_LOG_LINES))

        data = load_config()
        updated_projects = []
        found = False
        for p in self.projects:
            if p.get("path") == project_path and not found:
                proj = {
                    "path": project_path,
                    "name": project_name,
                    "framework": framework,
                    "php_path": php_path,
                    "php_service": php_service,
                    "db_service": db_service,
                    "server_port": server_port,
                    "use_docker": use_docker,
                    "yii_template": yii_template,
                    "log_dirs": paths,
                    "git_remote": git_remote,
                    "compose_files": self.compose_files,
                    "compose_profile": self.compose_profile,
                    "docker_project_path": self.docker_project_path,
                    "auto_refresh_secs": self.auto_refresh_secs,
                    "open_browser": self.open_browser,
                    "max_log_lines": self.max_log_lines,
                    "enable_terminal": self.enable_terminal,
                }
                updated_projects.append(proj)
                found = True
            else:
                temp = p.copy()
                temp.pop("show_console_output", None)
                updated_projects.append(temp)
        if not found:
            updated_projects.append(
                {
                    "path": project_path,
                    "name": project_name,
                    "framework": framework,
                    "php_path": php_path,
                    "php_service": php_service,
                    "db_service": db_service,
                    "server_port": server_port,
                    "use_docker": use_docker,
                    "yii_template": yii_template,
                    "log_dirs": paths,
                    "git_remote": git_remote,
                    "compose_files": self.compose_files,
                    "compose_profile": self.compose_profile,
                    "docker_project_path": self.docker_project_path,
                    "auto_refresh_secs": self.auto_refresh_secs,
                    "open_browser": self.open_browser,
                    "max_log_lines": self.max_log_lines,
                    "enable_terminal": self.enable_terminal,
                }
            )
        self.projects = updated_projects
        data.update(
            {
                "projects": self.projects,
                "current_project": project_path,
                "theme": self.theme_choice,
                "show_console_output": self.show_console_output,
                "enable_tray": self.tray_enabled,
            }
        )
        try:
            save_config(data)
        except OSError as e:
            print(f"Failed to write config: {e}")

        if self.follow_system_theme:
            apply_theme(self, self.os_theme)
            self.theme = self.os_theme
        else:
            apply_theme(self, self.theme_choice)
            self.theme = self.theme_choice
        print("Settings saved!")
        self.mark_settings_saved()
        if self.tray_enabled:
            self._init_tray_icon()
        elif self._tray_icon is not None:
            self._tray_icon.hide()

        if hasattr(self, "logs_tab"):
            self.logs_tab.update_timer_interval(self.auto_refresh_secs)
            if hasattr(self.logs_tab, "set_log_dirs"):
                self.logs_tab.set_log_dirs(self.log_dirs)

        if hasattr(self, "git_tab"):
            if self.is_git_repo:
                self.git_tab.load_branches()
            if hasattr(self.git_tab, "update_visibility"):
                self.git_tab.update_visibility()

    def artisan(self, *args: str) -> None:
        if not self.ensure_project_path():
            return
        base = self.docker_project_path if self.use_docker else self.project_path
        artisan_file = Path(base) / "artisan"
        self.run_command([self.php_path, str(artisan_file), *args])

    def symfony(self, *args: str) -> None:
        if not self.ensure_project_path():
            return
        base = self.docker_project_path if self.use_docker else self.project_path
        console = Path(base) / "bin" / "console"
        self.run_command([self.php_path, str(console), *args])

    def yii(self, *args: str) -> None:
        if not self.ensure_project_path():
            return
        base = self.docker_project_path if self.use_docker else self.project_path
        script = os.path.join(base, "yii")
        yii_bat = os.path.join(base, "yii.bat")
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
        if not self.ensure_project_path():
            return
        base = self.docker_project_path if self.use_docker else self.project_path
        phpunit_file = Path(base) / "vendor" / "bin" / "phpunit"
        self.run_command([self.php_path, str(phpunit_file)])

    def start_project(self) -> None:
        if self.project_running:
            print("Project already running")
            return

        if self.use_docker:
            if not self.ensure_project_path():
                return
            self.run_command(["docker", "compose", "up", "-d"])
            self.project_running = True
            self.update_run_buttons()
            self.update_window_title()
            self.notify("Project started")
            return

        if self.server_process and self.server_process.poll() is None:
            print("Project already running")
            return

        if not self.ensure_project_path():
            return

        if _port_in_use(self.server_port):
            QMessageBox.warning(
                self,
                APP_NAME,
                f"Port {self.server_port} is already in use.",
            )
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
            self.update_window_title()
            if self.open_browser:
                webbrowser.open(f"http://localhost:{self.server_port}")
            self.notify("Project started")
            if self.tray_enabled:
                self._update_tray_menu()
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")

    def stop_project(self) -> None:
        if self.use_docker:
            if not self.ensure_project_path():
                return
            self.run_command(["docker", "compose", "down"])
            self.project_running = False
            self.update_run_buttons()
            self.update_window_title()
            self.notify("Project stopped")
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
        self.update_window_title()
        self.notify("Project stopped")
        if self.tray_enabled:
            self._update_tray_menu()

    def closeEvent(self, event: "QCloseEvent | None") -> None:
        if event is not None and event.spontaneous() and self.tray_enabled:
            event.ignore()
            self.hide()
            self._update_tray_menu()
            return
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
        if self._tray_icon is not None:
            self._tray_icon.hide()
        super().closeEvent(event)

    def on_tab_changed(self, index: int) -> None:
        if index == getattr(self, "git_index", -1):
            if self.is_git_repo:
                self.git_tab.load_branches()
            if hasattr(self.git_tab, "update_visibility"):
                self.git_tab.update_visibility()

    def clear_output(self) -> None:
        self.output_view.clear()

    def clear_log_file(self) -> None:
        """Truncate the configured log file if it exists."""
        log_file = ""
        if self.log_dirs:
            expanded = expand_log_paths(self.project_path, [self.log_dirs[0]])
            log_file = expanded[0] if expanded else ""
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

    def open_file(self, path: str) -> None:
        """Open ``path`` using the system's default application."""
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
            return

        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
            return

        try:
            subprocess.Popen(["xdg-open", path])
        except FileNotFoundError:
            subprocess.Popen(["gio", "open", path])
