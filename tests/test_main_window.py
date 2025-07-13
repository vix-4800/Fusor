import builtins
import os
import subprocess
from pathlib import Path

import pytest
from PyQt6.QtCore import QTimer

import fusor.main_window as mw_module
from fusor.main_window import MainWindow

# ---------------------------------------------------------------------------
# Helpers & fixtures
# ---------------------------------------------------------------------------

class FakeLogView:
    def __init__(self):
        self.text = None

    def setPlainText(self, text: str):
        self.text = text

@pytest.fixture
def main_window(monkeypatch, qtbot):
    monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)

    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    yield win

    win.close()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMainWindow:
    def test_refresh_logs_no_project_path(self, main_window, monkeypatch):
        main_window.project_path = ""
        main_window.log_view = FakeLogView()

        closed = []
        monkeypatch.setattr(main_window, "close", lambda: closed.append(True), raising=True)

        def forbid(*_a, **_kw):
            raise AssertionError("unexpected FS access")

        monkeypatch.setattr(os.path, "exists", forbid, raising=True)
        monkeypatch.setattr(mw_module, "open", forbid, raising=True)

        main_window.refresh_logs()

        assert closed == [True]
        assert main_window.log_view.text is None

    def test_start_project_uses_configured_php(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.framework_choice = "None"
        if hasattr(main_window, "framework_combo"):
            main_window.framework_combo.setCurrentText("None")

        main_window.php_path = "/custom/php"

        captured = {}

        class DummyProcess:
            def poll(self):
                return None
            stdout: list[str] = []

        def fake_popen(cmd, **_kw):
            captured["cmd"] = cmd
            return DummyProcess()

        monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        main_window.start_project()

        assert captured["cmd"][0] == "/custom/php"

    def test_start_project_uses_docker_compose_up(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.use_docker = True

        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cmd"] = cmd
            class Result:
                stdout = ""
                stderr = ""
            return Result()

        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)
        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

        main_window.start_project()

        assert captured["cmd"] == ["docker", "compose", "up", "-d"]

    def test_stop_project_uses_docker_compose_down(self, main_window, monkeypatch):
        main_window.use_docker = True

        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cmd"] = cmd
            class Result:
                stdout = ""
                stderr = ""
            return Result()

        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)
        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

        main_window.stop_project()

        assert captured["cmd"] == ["docker", "compose", "down"]

    def test_php_field_disabled_when_docker_enabled(self, main_window, qtbot):
        # enable docker and ensure php path widgets become disabled
        main_window.docker_checkbox.setChecked(True)
        qtbot.wait(10)
        assert not main_window.php_path_edit.isEnabled()

        # disable docker again and widgets should be enabled
        main_window.docker_checkbox.setChecked(False)
        qtbot.wait(10)
        assert main_window.php_path_edit.isEnabled()
