import os
import subprocess
from pathlib import Path

import pytest
from PyQt6.QtCore import QTimer, Qt

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

    def test_start_project_uses_configured_port(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.framework_choice = "None"
        if hasattr(main_window, "framework_combo"):
            main_window.framework_combo.setCurrentText("None")

        main_window.server_port = 1234

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

        assert "localhost:1234" in captured["cmd"]

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

    def test_start_project_includes_compose_files(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.use_docker = True
        main_window.compose_files = ["a.yml", "b.yml"]

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

        assert captured["cmd"][:8] == [
            "docker",
            "compose",
            "-f",
            "a.yml",
            "-f",
            "b.yml",
            "up",
            "-d",
        ]

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

    def test_stop_project_includes_compose_files(self, main_window, monkeypatch):
        main_window.use_docker = True
        main_window.compose_files = ["a.yml", "b.yml"]

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

        assert captured["cmd"][:7] == [
            "docker",
            "compose",
            "-f",
            "a.yml",
            "-f",
            "b.yml",
            "down",
        ]

    def test_php_field_disabled_when_docker_enabled(self, main_window, qtbot):
        assert not main_window.tabs.isTabVisible(main_window.docker_index)
        assert not main_window.tabs.isTabEnabled(main_window.docker_index)

        # enable docker and ensure php path widgets become disabled
        main_window.docker_checkbox.setChecked(True)
        qtbot.wait(10)
        assert not main_window.php_path_edit.isEnabled()
        assert main_window.php_service_edit.isEnabled()
        assert main_window.tabs.isTabVisible(main_window.docker_index)
        assert main_window.tabs.isTabEnabled(main_window.docker_index)

        # disable docker again and widgets should be enabled and tab hidden
        main_window.docker_checkbox.setChecked(False)
        qtbot.wait(10)
        assert main_window.php_path_edit.isEnabled()
        assert not main_window.php_service_edit.isEnabled()
        assert not main_window.tabs.isTabVisible(main_window.docker_index)
        assert not main_window.tabs.isTabEnabled(main_window.docker_index)

    def test_composer_install_button_runs_command(self, main_window, qtbot, monkeypatch):
        captured = []
        monkeypatch.setattr(main_window, "run_command", lambda cmd: captured.append(cmd), raising=True)
        qtbot.mouseClick(main_window.project_tab.composer_install_btn, Qt.MouseButton.LeftButton)
        assert captured == [["composer", "install"]]

    def test_composer_update_button_runs_command(self, main_window, qtbot, monkeypatch):
        captured = []
        monkeypatch.setattr(main_window, "run_command", lambda cmd: captured.append(cmd), raising=True)
        qtbot.mouseClick(main_window.project_tab.composer_update_btn, Qt.MouseButton.LeftButton)
        assert captured == [["composer", "update"]]

    def test_run_command_uses_php_service_with_docker(self, main_window, monkeypatch):
        main_window.use_docker = True
        main_window.php_service = "myphp"
        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cmd"] = cmd
            class Result:
                stdout = ""
                stderr = ""
            return Result()

        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        main_window.run_command(["php", "-v"])

        assert captured["cmd"][:5] == ["docker", "compose", "exec", "-T", "myphp"]

    def test_run_command_adds_compose_files(self, main_window, monkeypatch):
        main_window.use_docker = True
        main_window.compose_files = ["a.yml", "b.yml"]
        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cmd"] = cmd
            class Result:
                stdout = ""
                stderr = ""
            return Result()

        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        main_window.run_command(["php", "-v"])

        assert captured["cmd"][:9] == [
            "docker",
            "compose",
            "-f",
            "a.yml",
            "-f",
            "b.yml",
            "exec",
            "-T",
            main_window.php_service,
        ]

    def test_refresh_logs_reads_custom_path(self, tmp_path: Path, main_window, monkeypatch):
        log_file = tmp_path / "custom.log"
        log_file.write_text("log text")
        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_path = "custom.log"

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(log_file)]
        assert main_window.log_view.text == "log text"

    def test_yii_template_row_visibility(self, main_window, qtbot):
        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert main_window.settings_tab.yii_template_row.isHidden()
        assert main_window.settings_tab.yii_template_label.isHidden()

        main_window.framework_combo.setCurrentText("Yii")
        qtbot.wait(10)
        assert not main_window.settings_tab.yii_template_row.isHidden()
        assert not main_window.settings_tab.yii_template_label.isHidden()

    def test_log_path_row_visibility(self, main_window, qtbot):
        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert main_window.settings_tab.log_path_row.isHidden()
        assert main_window.settings_tab.log_path_label.isHidden()

        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert not main_window.settings_tab.log_path_row.isHidden()
        assert not main_window.settings_tab.log_path_label.isHidden()

    def test_settings_unsaved_indicator(self, main_window, qtbot):
        idx = main_window.tabs.indexOf(main_window.settings_tab)
        assert main_window.tabs.tabText(idx) == "Settings"

        main_window.project_combo.setCurrentText("/tmp")
        main_window.project_path = "/tmp"
        main_window.php_path_edit.setText("/tmp/php")
        qtbot.wait(10)
        assert main_window.tabs.tabText(idx) == "Settings*"

        main_window.docker_checkbox.setChecked(True)
        main_window.mark_settings_saved()
        qtbot.wait(10)
        assert main_window.tabs.tabText(idx) == "Settings"
       
    def test_help_button_opens_dialog(self, main_window, qtbot, monkeypatch):
        shown = []

        def fake_exec(self):
            shown.append(self.windowTitle())

        monkeypatch.setattr(
            "fusor.about_dialog.AboutDialog.exec",
            fake_exec,
            raising=True,
        )

        qtbot.mouseClick(main_window.help_button, Qt.MouseButton.LeftButton)


        assert shown == ["About Fusor"]

    def test_clear_output_button_clears_text(self, main_window, qtbot):
        main_window.output_view.setPlainText("hello")

        qtbot.mouseClick(
            main_window.clear_output_button, Qt.MouseButton.LeftButton
        )

        assert main_window.output_view.toPlainText() == ""
