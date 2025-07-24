import fusor.main_window  # ensure SettingsTab can import without circular error
from fusor.tabs.settings_tab import SettingsTab
from PyQt6.QtWidgets import QFileDialog, QInputDialog
from PyQt6.QtCore import Qt
import subprocess

class DummyMainWindow:
    def __init__(self):
        self.projects = []
        self.project_path = ""
        self.framework_choice = "None"
        self.php_path = "php"
        self.php_service = "php"
        self.db_service = "db"
        self.server_port = 8000
        self.compose_files = []
        self.compose_profile = ""
        self.docker_project_path = "/app"
        self.use_docker = False
        self.yii_template = "basic"
        self.log_dirs = []
        self.auto_refresh_secs = 5
        self.theme = "dark"
        self.git_remote = ""
        self.enable_terminal = False
        self.tray_enabled = False
        self._tray_icon = None
        self.git_tab = type("G", (), {"get_remotes": lambda self: []})()
        self.database_tab = type("D", (), {"on_framework_changed": lambda self, t: None})()
        self.mark_settings_dirty = lambda *a, **k: None
        self.saved = False
        self.path = None

    def on_theme_combo_changed(self, text: str) -> None:
        pass

    def default_log_dirs(self, framework: str, template: str | None = None):
        return []

    def set_current_project(self, path: str):
        self.path = path
        self.project_path = path

    def save_settings(self):
        self.saved = True


def test_clone_project_runs_git_clone(monkeypatch, qtbot, tmp_path):
    main = DummyMainWindow()
    tab = SettingsTab(main)
    qtbot.addWidget(tab)

    texts = []
    responses = [("https://example.com/repo.git", True), ("proj", True)]

    def fake_get_text(*a, **k):
        texts.append(k.get("text", ""))
        return responses.pop(0)

    monkeypatch.setattr(QInputDialog, "getText", fake_get_text, raising=True)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tmp_path), raising=True)

    commands = []

    class DummyResult:
        def __init__(self):
            self.stdout = ""
            self.stderr = ""
            self.returncode = 0

    def fake_run(cmd, capture_output=True, text=True):
        commands.append(cmd)
        return DummyResult()

    monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

    qtbot.mouseClick(tab.clone_btn, Qt.MouseButton.LeftButton)

    assert len(texts) == 2
    assert commands[0] == ["git", "ls-remote", "https://example.com/repo.git"]
    assert commands[1] == ["git", "clone", "https://example.com/repo.git", str(tmp_path / "proj")]
    assert main.path == str(tmp_path / "proj")
    assert main.saved
