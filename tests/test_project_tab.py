import os
import sys
import subprocess
import json

from fusor.tabs.project_tab import ProjectTab

class DummyMainWindow:
    def __init__(self, path="/proj"):
        self.project_path = path
        # methods required by ProjectTab but unused in these tests
        self.start_project = lambda: None
        self.stop_project = lambda: None
        self.phpunit = lambda: None
        self.run_command = lambda *a, **k: None

def make_tab(qtbot):
    main = DummyMainWindow()
    tab = ProjectTab(main)
    qtbot.addWidget(tab)
    return tab, main

def capture_popen(monkeypatch):
    captured = {}

    def fake_popen(cmd, cwd=None):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        class D:
            pass
        return D()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    return captured

def test_open_terminal_macos(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    captured = capture_popen(monkeypatch)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)

    tab.open_terminal()

    assert captured["cmd"] == ["open", "-a", "Terminal", main.project_path]
    assert captured["cwd"] is None

def test_open_terminal_windows(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    captured = capture_popen(monkeypatch)
    monkeypatch.setattr(sys, "platform", "win32", raising=False)
    monkeypatch.setattr(os, "name", "nt", raising=False)

    tab.open_terminal()

    assert captured["cmd"] == ["cmd.exe"]
    assert captured["cwd"] == main.project_path

def test_open_terminal_linux(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    captured = capture_popen(monkeypatch)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)

    tab.open_terminal()

    assert captured["cmd"] == ["x-terminal-emulator"]
    assert captured["cwd"] == main.project_path

def test_open_explorer_windows(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    captured = {}
    monkeypatch.setattr(os, "startfile", lambda p: captured.setdefault("path", p), raising=False)
    monkeypatch.setattr(os, "name", "nt", raising=False)
    tab.open_explorer()
    assert captured["path"] == main.project_path

def test_open_explorer_macos(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    called = {}

    def fake_popen(cmd, *a, **kw):
        called["cmd"] = cmd
        class P: ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)
    tab.open_explorer()
    assert called["cmd"] == ["open", main.project_path]

def test_open_explorer_linux(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    cmds = []

    def fake_popen(cmd, *a, **kw):
        cmds.append(cmd)
        class P: ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)
    tab.open_explorer()
    assert cmds == [["xdg-open", main.project_path]]

def test_open_explorer_linux_fallback(monkeypatch, qtbot):
    tab, main = make_tab(qtbot)
    cmds = []

    def fake_popen(cmd, *a, **kw):
        cmds.append(cmd)
        if cmd[0] == "xdg-open":
            raise FileNotFoundError
        class P: ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)
    tab.open_explorer()
    assert cmds == [["xdg-open", main.project_path], ["gio", "open", main.project_path]]


def test_update_php_tools_enable_buttons(tmp_path, qtbot):
    data = {
        "require-dev": {
            "phpunit/phpunit": "*",
            "rector/rector": "*",
        }
    }
    (tmp_path / "composer.json").write_text(json.dumps(data))

    tab, main = make_tab(qtbot)
    main.project_path = str(tmp_path)
    tab.update_php_tools()

    assert tab.phpunit_btn.isEnabled()
    assert tab.rector_btn.isEnabled()
    assert not tab.csfixer_btn.isEnabled()


def test_update_php_tools_disable_without_composer(tmp_path, qtbot):
    tab, main = make_tab(qtbot)
    main.project_path = str(tmp_path)
    tab.update_php_tools()

    assert not tab.phpunit_btn.isEnabled()
    assert not tab.rector_btn.isEnabled()
    assert not tab.csfixer_btn.isEnabled()
