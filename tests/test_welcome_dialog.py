import subprocess

from fusor.welcome_dialog import WelcomeDialog
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget


class DummyMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.framework_choice = "Laravel"
        self.yii_template = "basic"
        self.saved = False
        self.path = None

    def set_current_project(self, path: str):
        self.path = path

    def save_settings(self):
        self.saved = True


def test_create_project_success(monkeypatch, qtbot, tmp_path):
    main = DummyMainWindow()
    dlg = WelcomeDialog(main)
    qtbot.addWidget(dlg)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tmp_path), raising=True)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("proj", True), raising=True)

    captured = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, capture_output=True, text=True, cwd=None):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

    dlg.create_project()

    expected = ["composer", "create-project", "laravel/laravel", str(tmp_path / "proj")]
    assert captured["cmd"] == expected
    assert captured["cwd"] is None
    assert main.path == str(tmp_path / "proj")
    assert main.saved


def test_create_project_failure(monkeypatch, qtbot, tmp_path):
    main = DummyMainWindow()
    dlg = WelcomeDialog(main)
    qtbot.addWidget(dlg)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tmp_path), raising=True)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("proj", True), raising=True)

    class Result:
        returncode = 1
        stdout = ""
        stderr = "boom"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Result(), raising=True)

    called = {}
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: called.setdefault("warn", True), raising=True)

    dlg.create_project()

    assert called.get("warn")
    assert main.path is None
    assert not main.saved
