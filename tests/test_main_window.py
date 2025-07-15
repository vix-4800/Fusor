import os
import subprocess
import shutil
from pathlib import Path

import pytest
from PyQt6.QtCore import QTimer, Qt

import fusor.main_window as mw_module
from fusor.main_window import MainWindow
from PyQt6.QtWidgets import QMainWindow, QPushButton
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

    def test_framework_tab_visibility(self, main_window, qtbot):
        assert main_window.tabs.isTabVisible(main_window.framework_index)
        assert main_window.tabs.isTabEnabled(main_window.framework_index)

        main_window.framework_combo.setCurrentText("None")
        qtbot.wait(10)
        assert not main_window.tabs.isTabVisible(main_window.framework_index)
        assert not main_window.tabs.isTabEnabled(main_window.framework_index)

        main_window.framework_combo.setCurrentText("Laravel")
        qtbot.wait(10)
        assert main_window.tabs.isTabVisible(main_window.framework_index)
        assert main_window.tabs.isTabEnabled(main_window.framework_index)

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
        log_file = tmp_path / "large.log"
        lines = [f"line {i}" for i in range(2000)]
        log_file.write_text("\n".join(lines))
        main_window.project_path = str(tmp_path)
        main_window.log_view = FakeLogView()
        main_window.log_path = "large.log"
        main_window.max_log_lines = 1000

        main_window.refresh_logs()

        result = main_window.log_view.text.splitlines()
        assert result == lines[-1000:]

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

        assert shown == ["About Fusor"]

    def test_remove_project_updates_config(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(
            mw_module,
            "load_config",
            lambda: {
                "projects": ["/one", "/two"],
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

        assert [win.project_combo.itemText(i) for i in range(win.project_combo.count())] == ["/two"]
        assert win.project_path == "/two"
        assert saved["projects"] == ["/two"]
        assert saved["current_project"] == "/two"
        win.close()

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
                "projects": ["/one", "/two"],
                "current_project": "/one",
                "project_settings": {
                    "/one": {"server_port": 8000},
                    "/two": {"server_port": 8001},
                },
            },
            raising=True,
        )

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        assert win.server_port == 8000
        assert win.server_port_edit.value() == 8000

        win.project_combo.setCurrentText("/two")
        qtbot.wait(10)

        assert win.server_port == 8001
        assert win.server_port_edit.value() == 8001
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

    def test_git_tab_loads_remote_on_first_show(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        calls = []

        def fake(self):
            calls.append(True)
            self.remote_branches_loaded = True

        monkeypatch.setattr(GitTab, "load_remote_branches", fake, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        assert not win.git_tab.remote_branches_loaded

        win.tabs.setCurrentIndex(win.git_index)
        qtbot.wait(10)

        assert calls == [True]

        win.tabs.setCurrentIndex(win.settings_index)
        qtbot.wait(10)
        win.tabs.setCurrentIndex(win.git_index)
        qtbot.wait(10)

        assert calls == [True]
        win.close()

    def test_git_refresh_button_triggers_load(self, qtbot, monkeypatch):
        monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
        monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
        monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

        calls = []

        def fake(self):
            calls.append(True)
            self.remote_branches_loaded = True

        monkeypatch.setattr(GitTab, "load_remote_branches", fake, raising=True)

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()

        win.tabs.setCurrentIndex(win.git_index)
        qtbot.wait(10)

        refresh_btn = None
        for btn in win.git_tab.findChildren(QPushButton):
            if btn.text() == "🔄 Refresh":
                refresh_btn = btn
                break
        assert refresh_btn is not None

        qtbot.mouseClick(refresh_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(10)

        assert calls == [True, True]
        win.close()

    def test_clear_log_button_truncates_file(self, tmp_path: Path, main_window, qtbot):
        log_file = tmp_path / "app.log"
        log_file.write_text("hello")
        main_window.project_path = str(tmp_path)
        main_window.log_path = "app.log"

        qtbot.mouseClick(main_window.logs_tab.clear_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(10)

        assert log_file.read_text() == ""

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
