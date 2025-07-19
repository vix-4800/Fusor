from fusor.tabs.settings_tab import SettingsTab
from PyQt6.QtWidgets import QFileDialog


class DummyMainWindow:
    def __init__(self):
        self.projects = []
        self.project_path = ""
        self.framework_choice = "None"
        self.php_path = "php"
        self.php_service = "php"
        self.server_port = 8000
        self.compose_files = []
        self.compose_profile = ""
        self.docker_project_path = "/app"
        self.use_docker = False
        self.yii_template = "basic"
        self.log_paths = []
        self.auto_refresh_secs = 5
        self.theme = "dark"
        self.git_remote = ""
        self.enable_terminal = False
        self.git_tab = type("G", (), {"get_remotes": lambda self: []})()
        self.database_tab = type("D", (), {"on_framework_changed": lambda self, t: None})()
        self.mark_settings_dirty = lambda *a, **k: None

    def default_log_paths(self, framework: str, template: str | None = None):
        return []

    def set_current_project(self, path: str):
        self.project_path = path

    def save_settings(self):
        pass


def test_add_project_detects_symfony(tmp_path, monkeypatch, qtbot):
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "console").touch()

    main = DummyMainWindow()
    tab = SettingsTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *a, **k: str(tmp_path),
        raising=True,
    )

    tab.add_project()

    assert tab.framework_combo.currentText() == "Symfony"
    assert main.project_path == str(tmp_path)

