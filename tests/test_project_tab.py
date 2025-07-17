import os
import sys
import subprocess

from fusor.tabs.project_tab import ProjectTab


class DummyMainWindow:
    def __init__(self, path="/proj"):
        self.project_path = path

    # required by ProjectTab constructor
    def start_project(self):
        pass

    def stop_project(self):
        pass

    def phpunit(self):
        pass

    def run_command(self, cmd):
        pass


def create_tab(qtbot):
    main = DummyMainWindow()
    tab = ProjectTab(main)
    qtbot.addWidget(tab)
    return tab, main


def test_open_explorer_windows(monkeypatch, qtbot):
    tab, main = create_tab(qtbot)
    captured = {}
    monkeypatch.setattr(os, "startfile", lambda p: captured.setdefault("path", p), raising=False)
    monkeypatch.setattr(os, "name", "nt", raising=False)
    tab.open_explorer()
    assert captured["path"] == main.project_path


def test_open_explorer_macos(monkeypatch, qtbot):
    tab, main = create_tab(qtbot)
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
    tab, main = create_tab(qtbot)
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
    tab, main = create_tab(qtbot)
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
