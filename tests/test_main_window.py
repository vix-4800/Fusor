import os
import sys
import subprocess
import shutil
from pathlib import Path
import webbrowser

import pytest
from PyQt6.QtCore import QTimer, Qt

import fusor.main_window as mw_module
from fusor.main_window import MainWindow
from fusor import APP_NAME
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from fusor.tabs.git_tab import GitTab

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
    monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

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

        shown = []

        class DummyDlg:
            def exec(self):
                shown.append(True)

        monkeypatch.setattr(mw_module, "WelcomeDialog", lambda *a, **k: DummyDlg(), raising=True)

        def forbid(*_a, **_kw):
            raise AssertionError("unexpected FS access")

        monkeypatch.setattr(os.path, "exists", forbid, raising=True)
        monkeypatch.setattr(mw_module, "open", forbid, raising=True)

        main_window.refresh_logs()

        assert closed == []
        assert shown == [True]
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
        main_window.project_path = "/repo"

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
        main_window.project_path = "/repo"

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

    def test_laravel_tab_visibility(self, main_window, qtbot):
        assert main_window.tabs.isTabVisible(main_window.laravel_index)
        assert main_window.tabs.isTabEnabled(main_window.laravel_index)

        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert not main_window.tabs.isTabVisible(main_window.laravel_index)
        assert not main_window.tabs.isTabEnabled(main_window.laravel_index)

        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert main_window.tabs.isTabVisible(main_window.laravel_index)
        assert main_window.tabs.isTabEnabled(main_window.laravel_index)

    def test_symfony_tab_visibility(self, main_window, qtbot):
        assert not main_window.tabs.isTabVisible(main_window.symfony_index)
        assert not main_window.tabs.isTabEnabled(main_window.symfony_index)

        main_window.framework_combo.setCurrentText("Symfony")
        qtbot.wait(10)
        assert main_window.tabs.isTabVisible(main_window.symfony_index)
        assert main_window.tabs.isTabEnabled(main_window.symfony_index)

        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert not main_window.tabs.isTabVisible(main_window.symfony_index)
        assert not main_window.tabs.isTabEnabled(main_window.symfony_index)

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

    def test_run_command_sets_cwd_when_using_docker(self, main_window, monkeypatch):
        main_window.use_docker = True
        main_window.project_path = "/repo"
        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cwd"] = cwd
            return type("R", (), {"stdout": "", "stderr": ""})()

        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        main_window.run_command(["php", "-v"])

        assert captured["cwd"] == "/repo"

    def test_run_command_sets_cwd_without_docker(self, main_window, monkeypatch):
        main_window.use_docker = False
        main_window.project_path = "/repo"
        captured = {}

        def fake_run(cmd, capture_output=True, text=True, cwd=None):
            captured["cwd"] = cwd
            return type("R", (), {"stdout": "", "stderr": ""})()

        monkeypatch.setattr(subprocess, "run", fake_run, raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        main_window.run_command(["echo", "hi"])

        assert captured["cwd"] == "/repo"

    def test_refresh_logs_reads_custom_path(self, tmp_path: Path, main_window, monkeypatch):
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        log_file = log_dir / "custom.log"
        log_file.write_text("log text")
        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_dirs = ["logs"]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(log_file)]
        assert main_window.log_view.text == "log text"

    def test_refresh_logs_reads_yii_basic_logs(self, tmp_path: Path, main_window, monkeypatch):
        log_file = tmp_path / "runtime" / "log" / "app.log"
        log_file.parent.mkdir(parents=True)
        log_file.write_text("basic log")
        main_window.project_path = str(tmp_path)
        main_window.framework_choice = "Yii"
        if hasattr(main_window, "framework_combo"):
            main_window.framework_combo.setCurrentText("Yii")
        main_window.yii_template = "basic"
        if hasattr(main_window, "yii_template_combo"):
            main_window.yii_template_combo.setCurrentText("basic")
        main_window.log_view = FakeLogView()

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(log_file)]
        assert "basic log" in main_window.log_view.text

    def test_refresh_logs_reads_yii_advanced_logs(self, tmp_path: Path, main_window, monkeypatch):
        files = []
        for part in ["frontend", "backend", "console"]:
            f = tmp_path / part / "runtime" / "logs" / "app.log"
            f.parent.mkdir(parents=True)
            f.write_text(f"{part} log")
            files.append(f)
        main_window.project_path = str(tmp_path)
        main_window.framework_choice = "Yii"
        if hasattr(main_window, "framework_combo"):
            main_window.framework_combo.setCurrentText("Yii")
        main_window.yii_template = "advanced"
        if hasattr(main_window, "yii_template_combo"):
            main_window.yii_template_combo.setCurrentText("advanced")
        main_window.log_view = FakeLogView()

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(f) for f in files]
        for part in ["frontend", "backend", "console"]:
            assert f"{part} log" in main_window.log_view.text

    def test_refresh_logs_truncates_large_files(self, tmp_path: Path, main_window):
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        log_file = log_dir / "large.log"
        lines = [f"line {i}" for i in range(2000)]
        log_file.write_text("\n".join(lines))
        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_dirs = ["logs"]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)
        main_window.max_log_lines = 1000

        main_window.refresh_logs()

        result = main_window.log_view.text.splitlines()
        assert result == lines[-1000:]

    def test_refresh_logs_reads_all_configured_files(self, tmp_path: Path, main_window, monkeypatch):
        paths = []
        for i in range(3):
            d = tmp_path / f"dir{i}"
            d.mkdir()
            p = d / "app.log"
            p.write_text(f"msg{i}")
            paths.append(p)

        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_dirs = [f"dir{i}" for i in range(3)]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(p) for p in paths]
        for i in range(3):
            assert f"msg{i}" in main_window.log_view.text

    def test_refresh_logs_reads_directory(self, tmp_path: Path, main_window, monkeypatch):
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        files = []
        for i in range(2):
            f = logs_dir / f"log{i}.log"
            f.write_text(f"msg{i}")
            files.append(f)

        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_dirs = ["logs"]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)

        opened = []
        real_open = mw_module.open

        def fake_open(path, *args, **kwargs):
            opened.append(path)
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(mw_module, "open", fake_open, raising=True)

        main_window.refresh_logs()

        assert opened == [str(p) for p in files]
        for i in range(2):
            assert f"msg{i}" in main_window.log_view.text

    def test_yii_template_row_visibility(self, main_window, qtbot):
        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert main_window.settings_tab.yii_template_row.isHidden()
        assert main_window.settings_tab.yii_template_label.isHidden()

        main_window.framework_combo.setCurrentText("Yii")
        qtbot.wait(10)
        assert not main_window.settings_tab.yii_template_row.isHidden()
        assert not main_window.settings_tab.yii_template_label.isHidden()

    def test_log_dir_row_visibility(self, main_window, qtbot):
        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert main_window.settings_tab.log_dirs_container.isHidden()
        assert main_window.settings_tab.log_dir_label.isHidden()

        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert not main_window.settings_tab.log_dirs_container.isHidden()
        assert not main_window.settings_tab.log_dir_label.isHidden()

        main_window.framework_combo.setCurrentText("Symfony")
        qtbot.wait(10)
        assert not main_window.settings_tab.log_dirs_container.isHidden()
        assert not main_window.settings_tab.log_dir_label.isHidden()

        main_window.framework_combo.setCurrentText("Yii")
        qtbot.wait(10)
        assert not main_window.settings_tab.log_dirs_container.isHidden()
        assert not main_window.settings_tab.log_dir_label.isHidden()

    def test_default_log_dirs_per_framework(self, main_window, qtbot):
        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert main_window.settings_tab.log_dir_edits[0].text() == str(Path("storage") / "logs")

        main_window.framework_combo.setCurrentText("Symfony")
        qtbot.wait(10)
        assert main_window.settings_tab.log_dir_edits[0].text() == str(Path("var") / "log")

        main_window.framework_combo.setCurrentText("Yii")
        main_window.yii_template_combo.setCurrentText("basic")
        qtbot.wait(10)
        assert main_window.settings_tab.log_dir_edits[0].text() == str(Path("runtime") / "log")

    def test_settings_unsaved_indicator(self, main_window, qtbot):
        idx = main_window.tabs.indexOf(main_window.settings_tab)
        assert main_window.tabs.tabText(idx) == "Settings"

        main_window.project_combo.addItem("/tmp")
        main_window.project_combo.addItem("/tmp")
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

        assert shown == [f"About {APP_NAME}"]

    def test_remove_project_updates_config(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            mw_module,
            "load_config",
            lambda: {
                "projects": [
                    {"path": "/one", "name": "one"},
                    {"path": "/two", "name": "two"},
                ],
                "current_project": "/one",
            },
            raising=True,
        )
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)
        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        monkeypatch.setattr(os.path, "isfile", lambda p: True, raising=True)
        monkeypatch.setattr(
            "PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **k: None, raising=True
        )

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        qtbot.mouseClick(win.settings_tab.remove_btn, Qt.MouseButton.LeftButton)

        assert [win.project_combo.itemText(i) for i in range(win.project_combo.count())] == ["two"]
        assert win.project_path == "/two"
        assert saved["projects"] == [{"path": "/two", "name": "two"}]
        assert saved["current_project"] == "/two"
        win.close()

    def test_remove_last_project(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            "fusor.tabs.settings_tab.load_config",
            lambda: {
                "projects": [{"path": "/one", "name": "one"}],
                "current_project": "/one",
                "project_settings": {"/one": {"server_port": 8000}},
            },
            raising=True,
        )
        saved = {}
        monkeypatch.setattr("fusor.tabs.settings_tab.save_config", lambda data: saved.update(data), raising=True)
        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        monkeypatch.setattr(os.path, "isfile", lambda p: True, raising=True)
        monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **k: None, raising=True)
        shown = []
        monkeypatch.setattr(MainWindow, "show_welcome_dialog", lambda self: shown.append(True), raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        qtbot.mouseClick(win.settings_tab.remove_btn, Qt.MouseButton.LeftButton)

        assert win.project_combo.count() == 0
        assert win.project_path == ""
        assert saved["projects"] == []
        assert saved["current_project"] == ""
        assert "/one" not in saved.get("project_settings", {})
        assert shown
        win.close()

    def test_exit_when_welcome_dialog_closed_without_project(self, main_window, monkeypatch):
        closed = []
        monkeypatch.setattr(main_window, "close", lambda: closed.append(True), raising=True)

        class DummyDlg:
            def exec(self):
                return 0

        monkeypatch.setattr(mw_module, "WelcomeDialog", lambda *a, **k: DummyDlg(), raising=True)

        main_window.projects = []
        main_window.project_path = ""

        main_window.show_welcome_dialog()

        assert closed == [True]

    def test_clear_output_button_clears_text(self, main_window, qtbot):
        main_window.output_view.setPlainText("hello")

        qtbot.mouseClick(
            main_window.clear_output_button, Qt.MouseButton.LeftButton
        )

        assert main_window.output_view.toPlainText() == ""

    def test_save_settings_accepts_executable_name(self, main_window, monkeypatch):
        main_window.project_combo.addItem("/tmp")
        main_window.project_combo.setCurrentText("/tmp")
        main_window.project_path = "/tmp"
        main_window.php_path_edit.setText("php")
        main_window.docker_checkbox.setChecked(False)
        main_window.server_port_edit.setValue(8000)

        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        monkeypatch.setattr(os.path, "isfile", lambda p: False, raising=True)
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/php" if cmd == "php" else None, raising=True)

        warnings = []
        monkeypatch.setattr(
            "PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **k: warnings.append(True), raising=True
        )
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)

        main_window.save_settings()

        assert not warnings
        assert saved["project_settings"]["/tmp"]["php_path"] == "php"

    def test_project_change_updates_settings(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            mw_module,
            "load_config",
            lambda: {
                "projects": [
                    {"path": "/one", "name": "one"},
                    {"path": "/two", "name": "two"},
                ],
                "current_project": "/one",
                "project_settings": {
                    "/one": {"server_port": 8000},
                    "/two": {"server_port": 8001},
                },
            },
            raising=True,
        )
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        assert win.server_port == 8000
        assert win.server_port_edit.value() == 8000

        win.project_combo.setCurrentText("two")
        qtbot.wait(10)

        assert win.server_port == 8001
        assert win.server_port_edit.value() == 8001
        win.close()

    def test_project_change_clears_log_view(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            mw_module,
            "load_config",
            lambda: {
                "projects": [
                    {"path": "/one", "name": "one"},
                    {"path": "/two", "name": "two"},
                ],
                "current_project": "/one",
            },
            raising=True,
        )
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        win.log_view = FakeLogView()
        win.log_view.setPlainText("old")

        win.project_combo.setCurrentText("two")
        qtbot.wait(10)

        assert win.log_view.text == ""
        win.close()

    def test_open_terminal_launches_with_project_cwd(self, tmp_path: Path, main_window, qtbot, monkeypatch):
        main_window.project_path = str(tmp_path)

        captured = {}

        def fake_popen(cmd, cwd=None, *a, **kw):
            captured["cmd"] = cmd
            captured["cwd"] = cwd
            class Dummy:
                pass
            return Dummy()

        monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)

        qtbot.mouseClick(main_window.project_tab.terminal_btn, Qt.MouseButton.LeftButton)

        assert captured["cwd"] == str(tmp_path)
        expected_cmd = ["cmd.exe"] if os.name == "nt" else ["x-terminal-emulator"]
        assert captured["cmd"] == expected_cmd

    def test_geometry_loaded_from_config(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            mw_module,
            "load_config",
            lambda: {"window_size": [640, 480], "window_position": [30, 40]},
            raising=True,
        )
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)
        called = {}
        orig_resize = QMainWindow.resize
        orig_move = QMainWindow.move

        def fake_resize(self, w, h):
            called["resize"] = (w, h)
            orig_resize(self, w, h)

        def fake_move(self, x, y):
            called["move"] = (x, y)
            orig_move(self, x, y)

        monkeypatch.setattr(QMainWindow, "resize", fake_resize, raising=True)
        monkeypatch.setattr(QMainWindow, "move", fake_move, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        assert called["resize"] == (640, 480)
        assert called["move"] == (30, 40)
        win.close()

    def test_close_event_saves_geometry(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()
        qtbot.wait(10)
        win.resize(777, 555)
        win.move(11, 22)
        monkeypatch.setattr(win, "width", lambda: 777, raising=True)
        monkeypatch.setattr(win, "height", lambda: 555, raising=True)
        monkeypatch.setattr(win, "x", lambda: 11, raising=True)
        monkeypatch.setattr(win, "y", lambda: 22, raising=True)
        win.close()

        assert saved["window_size"] == [777, 555]
        assert saved["window_position"] == [11, 22]

    def test_stdout_restored_after_close(self, qtbot, monkeypatch, capsys):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        original = sys.stdout

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()
        qtbot.wait(10)
        win.close()

        assert sys.stdout is original
        print("restored")
        out = capsys.readouterr().out
        assert "restored" in out

    def test_git_tab_loads_branches_on_first_show(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        calls = []

        def fake(self):
            calls.append(True)

        monkeypatch.setattr(GitTab, "load_branches", fake, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        win.tabs.setCurrentIndex(win.git_index)
        qtbot.wait(10)

        assert calls == [True]

        win.tabs.setCurrentIndex(win.settings_index)
        qtbot.wait(10)
        win.tabs.setCurrentIndex(win.git_index)
        qtbot.wait(10)

        assert calls == [True, True]
        win.close()


    def test_clear_log_button_truncates_file(self, tmp_path: Path, main_window, qtbot, monkeypatch):
        logs = tmp_path / "logs"
        logs.mkdir()
        log_file = logs / "app.log"
        log_file.write_text("hello")
        main_window.project_path = str(tmp_path)
        main_window.log_dirs = ["logs"]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)

        monkeypatch.setattr(
            "PyQt6.QtWidgets.QMessageBox.question",
            lambda *a, **k: QMessageBox.StandardButton.Yes,
            raising=True,
        )

        qtbot.mouseClick(main_window.logs_tab.clear_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(10)

        assert log_file.read_text() == ""

    def test_clear_log_button_aborts_on_no(self, tmp_path: Path, main_window, qtbot, monkeypatch):
        logs = tmp_path / "logs"
        logs.mkdir()
        log_file = logs / "app.log"
        log_file.write_text("hello")
        main_window.project_path = str(tmp_path)
        main_window.log_dirs = ["logs"]
        main_window.logs_tab.set_log_dirs(main_window.log_dirs)

        monkeypatch.setattr(
            "PyQt6.QtWidgets.QMessageBox.question",
            lambda *a, **k: QMessageBox.StandardButton.No,
            raising=True,
        )

        qtbot.mouseClick(main_window.logs_tab.clear_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(10)

        assert log_file.read_text() == "hello"

    def test_theme_applied_from_config(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {"theme": "light"}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        assert win.styleSheet() == mw_module.LIGHT_STYLESHEET
        win.close()

    def test_save_settings_persists_theme(self, main_window, monkeypatch):
        main_window.project_combo.addItem("/tmp")
        main_window.project_combo.setCurrentText("/tmp")
        main_window.project_path = "/tmp"
        main_window.theme_combo.setCurrentText("Light")

        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        monkeypatch.setattr(os.path, "isfile", lambda p: False, raising=True)
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/php" if cmd == "php" else None, raising=True)
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)

        main_window.save_settings()

        assert saved["theme"] == "light"
        assert main_window.styleSheet() == mw_module.LIGHT_STYLESHEET

    def test_save_settings_strips_compose_files(self, main_window, monkeypatch):
        main_window.project_combo.addItem("/tmp")
        main_window.project_combo.setCurrentText("/tmp")
        main_window.project_path = "/tmp"
        main_window.docker_checkbox.setChecked(True)
        main_window.settings_tab.add_compose_btn.click()
        main_window.settings_tab.compose_file_edits[0].setText(" a.yml ")
        main_window.settings_tab.compose_file_edits[1].setText(" b.yml  ")

        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)

        main_window.save_settings()

        assert main_window.compose_files == ["a.yml", "b.yml"]
        assert saved["project_settings"]["/tmp"]["compose_files"] == ["a.yml", "b.yml"]

    def test_save_settings_updates_project_name(self, main_window, monkeypatch):
        main_window.project_combo.addItem("/tmp", "/tmp")
        main_window.project_combo.setCurrentIndex(0)
        main_window.project_path = "/tmp"
        main_window.project_name_edit.setText("MyProj")
        main_window.php_path_edit.setText("php")
        main_window.docker_checkbox.setChecked(False)
        main_window.server_port_edit.setValue(8000)

        monkeypatch.setattr(os.path, "isdir", lambda p: True, raising=True)
        monkeypatch.setattr(os.path, "isfile", lambda p: False, raising=True)
        monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/php" if cmd == "php" else None, raising=True)
        saved = {}
        monkeypatch.setattr(mw_module, "save_config", lambda data: saved.update(data), raising=True)

        main_window.save_settings()

        assert main_window.projects == [{"path": "/tmp", "name": "MyProj"}]
        assert saved["projects"] == [{"path": "/tmp", "name": "MyProj"}]
        assert main_window.project_combo.itemText(0) == "MyProj"

    def test_start_project_includes_compose_profile(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.use_docker = True
        main_window.compose_profile = "dev"

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

        assert captured["cmd"] == [
            "docker",
            "compose",
            "--profile",
            "dev",
            "up",
            "-d",
        ]

    def test_start_project_opens_browser(self, tmp_path: Path, main_window, monkeypatch):
        main_window.project_path = str(tmp_path)
        (tmp_path / "public").mkdir()

        main_window.framework_choice = "None"
        if hasattr(main_window, "framework_combo"):
            main_window.framework_combo.setCurrentText("None")

        main_window.open_browser = True

        class DummyProcess:
            def poll(self):
                return None

            stdout: list[str] = []

        monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: DummyProcess(), raising=True)
        monkeypatch.setattr(main_window.executor, "submit", lambda fn: fn(), raising=True)

        opened = []
        monkeypatch.setattr(webbrowser, "open", lambda url: opened.append(url), raising=True)

        main_window.start_project()

        assert opened == [f"http://localhost:{main_window.server_port}"]

    def test_output_hidden_on_small_window(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        win.resize(400, 300)
        qtbot.wait(10)

        assert not win.output_view.isVisible()
        assert not win.clear_output_button.isVisible()

        win.resize(900, 700)
        qtbot.wait(10)

        assert win.output_view.isVisible()
        assert win.clear_output_button.isVisible()

    def test_minimum_window_size(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)

        assert win.minimumWidth() == 400
        assert win.minimumHeight() == 300
