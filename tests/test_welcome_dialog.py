from fusor.welcome_dialog import WelcomeDialog
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget


class DummyMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.framework_choice = "Laravel"
        self.yii_template = "basic"
        self.saved = False
        self.path = None
        self.cmd = None

    def set_current_project(self, path: str):
        self.path = path

    def save_settings(self):
        self.saved = True

    def run_command(self, cmd, callback=None):
        self.cmd = cmd
        if callback:
            callback()


def test_create_project_laravel(monkeypatch, qtbot, tmp_path):
    main = DummyMainWindow()
    dlg = WelcomeDialog(main)
    qtbot.addWidget(dlg)

    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("proj", True), raising=True)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tmp_path), raising=True)
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("Laravel", True), raising=True)

    dlg.create_project()

    expected = ["composer", "create-project", "laravel/laravel", str(tmp_path / "proj")]
    assert main.cmd == expected
    assert main.path == str(tmp_path / "proj")
    assert main.saved


def test_create_project_existing_path(monkeypatch, qtbot, tmp_path):
    main = DummyMainWindow()
    dlg = WelcomeDialog(main)
    qtbot.addWidget(dlg)

    dest = tmp_path / "proj"
    dest.mkdir()

    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("proj", True), raising=True)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tmp_path), raising=True)
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("Laravel", True), raising=True)

    called = {}
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: called.setdefault("warn", True), raising=True)

    dlg.create_project()

    assert called.get("warn")
    assert main.cmd is None
    assert main.path is None
    assert not main.saved

