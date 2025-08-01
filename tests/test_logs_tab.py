from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QColor
import os
import sys
import subprocess
import fusor.tabs.logs_tab as logs_tab

from fusor.tabs.logs_tab import LogsTab

class DummyMainWindow:
    def __init__(self):
        self.auto_refresh_secs = 12
        self.log_dirs = ["logs"]
        self.project_path = ""
    def refresh_logs(self):
        pass
    def clear_log_file(self):
        pass
    def open_file(self, path: str):
        pass

def test_timer_interval(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    assert tab._timer.interval() == 12000
    assert "12s" in tab.auto_checkbox.text()

def test_search_highlights_first_match(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    text = "foo bar foo"
    tab.log_view.setPlainText(text)
    tab.search_edit.setText("foo")

    qtbot.mouseClick(tab.search_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    cursor = tab.log_view.textCursor()
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    assert text[start:end] == "foo"
    assert start == text.find("foo")


def test_search_cycle_multiple_matches(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    text = "foo bar foo bar foo"
    tab.log_view.setPlainText(text)
    tab.search_edit.setText("foo")

    qtbot.mouseClick(tab.search_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert tab._search_positions == [0, 8, 16]
    assert tab.next_btn.isEnabled()
    assert tab.prev_btn.isEnabled()

    def current_start():
        c = tab.log_view.textCursor()
        return c.selectionStart()

    qtbot.mouseClick(tab.next_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    assert current_start() == 8

    qtbot.mouseClick(tab.next_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    assert current_start() == 16

    qtbot.mouseClick(tab.next_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    assert current_start() == 0

    qtbot.mouseClick(tab.prev_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)
    assert current_start() == 16


def test_search_empty_clears_highlighting(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    text = "foo bar foo"
    tab.log_view.setPlainText(text)

    tab.search_edit.setText("foo")
    qtbot.mouseClick(tab.search_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert tab.log_view.extraSelections()
    assert tab.next_btn.isEnabled()
    assert tab.prev_btn.isEnabled()

    tab.search_edit.setText("")
    qtbot.mouseClick(tab.search_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10)

    assert tab.log_view.extraSelections() == []
    assert not tab.next_btn.isEnabled()
    assert not tab.prev_btn.isEnabled()

def test_auto_refresh_truncates_large_file(tmp_path, qtbot, monkeypatch):
    from PyQt6.QtCore import QTimer
    from fusor import main_window as mw_module
    from fusor.main_window import MainWindow

    monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
    monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    win.project_path = str(tmp_path)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    win.log_dirs = [str(log_dir)]
    win.logs_tab.set_log_dirs(win.log_dirs)
    win.max_log_lines = 1000

    lines = [f"line {i}" for i in range(2000)]
    (log_dir / "big.log").write_text("\n".join(lines))

    win.logs_tab.auto_checkbox.setChecked(True)
    qtbot.wait(10)

    result = win.log_view.toPlainText().splitlines()
    assert result == lines[-1000:]

def test_responsive_layout_hides_log_view(qtbot):
    main = DummyMainWindow()
    tab = LogsTab(main)
    qtbot.addWidget(tab)
    tab.show()

    tab.update_responsive_layout(400)
    assert not tab.log_view.isVisible()
    assert not tab.prev_btn.isVisible()
    assert not tab.next_btn.isVisible()

    tab.update_responsive_layout(800)
    assert tab.log_view.isVisible()
    assert tab.prev_btn.isVisible()
    assert tab.next_btn.isVisible()
    
def test_set_log_dirs_expands_directory(tmp_path, qtbot):
    logs = tmp_path / "logs"
    logs.mkdir()
    for i in range(2):
        (logs / f"log{i}.log").write_text("")

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    main.log_dirs = [str(logs)]
    tab = LogsTab(main)
    qtbot.addWidget(tab)

    items = [tab.log_selector.itemText(i) for i in range(tab.log_selector.count())]
    expected = [str(logs / f"log{i}.log") for i in range(2)]
    assert items == expected


def _make_tab_for_open(tmp_path, qtbot):
    log_file = tmp_path / "test.log"
    log_file.write_text("")
    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    main.log_dirs = [str(log_file)]
    from fusor.main_window import MainWindow
    main.open_file = MainWindow.open_file.__get__(main, DummyMainWindow)
    tab = LogsTab(main)
    qtbot.addWidget(tab)
    return tab, main, log_file


def test_open_file_windows(monkeypatch, qtbot, tmp_path):
    tab, main, log_file = _make_tab_for_open(tmp_path, qtbot)

    captured = {}
    monkeypatch.setattr(os, "startfile", lambda p: captured.setdefault("path", p), raising=False)
    monkeypatch.setattr(os, "name", "nt", raising=False)
    import pathlib
    monkeypatch.setattr(logs_tab, "Path", pathlib.PosixPath)
    monkeypatch.setattr(logs_tab, "PurePath", pathlib.PurePosixPath)

    qtbot.mouseClick(tab.open_btn, Qt.MouseButton.LeftButton)

    assert captured["path"] == str(log_file)


def test_open_file_macos(monkeypatch, qtbot, tmp_path):
    tab, main, log_file = _make_tab_for_open(tmp_path, qtbot)

    called = {}

    def fake_popen(cmd, *a, **kw):
        called["cmd"] = cmd
        class P:
            ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)

    qtbot.mouseClick(tab.open_btn, Qt.MouseButton.LeftButton)

    assert called["cmd"] == ["open", str(log_file)]


def test_open_file_linux(monkeypatch, qtbot, tmp_path):
    tab, main, log_file = _make_tab_for_open(tmp_path, qtbot)

    cmds = []

    def fake_popen(cmd, *a, **kw):
        cmds.append(cmd)
        class P:
            ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)

    qtbot.mouseClick(tab.open_btn, Qt.MouseButton.LeftButton)

    assert cmds == [["xdg-open", str(log_file)]]


def test_open_file_linux_fallback(monkeypatch, qtbot, tmp_path):
    tab, main, log_file = _make_tab_for_open(tmp_path, qtbot)

    cmds = []

    def fake_popen(cmd, *a, **kw):
        cmds.append(cmd)
        if cmd[0] == "xdg-open":
            raise FileNotFoundError
        class P:
            ...
        return P()

    monkeypatch.setattr(subprocess, "Popen", fake_popen, raising=True)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)
    monkeypatch.setattr(os, "name", "posix", raising=False)

    qtbot.mouseClick(tab.open_btn, Qt.MouseButton.LeftButton)

    assert cmds == [["xdg-open", str(log_file)], ["gio", "open", str(log_file)]]


def _make_window_with_log(tmp_path, qtbot, monkeypatch, lines):
    from PyQt6.QtCore import QTimer
    from fusor import main_window as mw_module
    from fusor.main_window import MainWindow

    monkeypatch.setattr(QTimer, "singleShot", lambda *a, **k: None, raising=True)
    monkeypatch.setattr(mw_module, "load_config", lambda: {}, raising=True)
    monkeypatch.setattr(mw_module, "save_config", lambda *a, **k: None, raising=True)

    win = MainWindow()
    qtbot.addWidget(win)
    win.show()

    win.project_path = str(tmp_path)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "app.log"
    log_file.write_text("\n".join(lines))
    win.log_dirs = [str(log_dir)]
    win.logs_tab.set_log_dirs(win.log_dirs)

    return win, log_file


def test_refresh_logs_filters_by_level(tmp_path, qtbot, monkeypatch):
    lines = [
        "DEBUG debug msg",
        "INFO info msg",
        "WARNING warn msg",
        "ERROR error msg",
        "CRITICAL crit msg",
    ]

    win, _ = _make_window_with_log(tmp_path, qtbot, monkeypatch, lines)
    win.logs_tab.level_selector.setCurrentText("WARNING")

    win.refresh_logs()

    result = win.log_view.toPlainText().splitlines()
    assert result == lines[2:]


def test_refresh_logs_level_all_shows_everything(tmp_path, qtbot, monkeypatch):
    lines = [
        "DEBUG debug msg",
        "INFO info msg",
        "WARNING warn msg",
        "ERROR error msg",
        "CRITICAL crit msg",
    ]

    win, _ = _make_window_with_log(tmp_path, qtbot, monkeypatch, lines)
    win.logs_tab.level_selector.setCurrentText("All")

    win.refresh_logs()

    result = win.log_view.toPlainText().splitlines()
    assert result == lines


def test_refresh_logs_colors_levels(tmp_path, qtbot, monkeypatch):
    lines = [
        "DEBUG debug msg",
        "INFO info msg",
        "WARNING warn msg",
        "ERROR error msg",
        "CRITICAL crit msg",
    ]

    win, _ = _make_window_with_log(tmp_path, qtbot, monkeypatch, lines)
    win.refresh_logs()
    qtbot.wait(10)

    cursor = win.log_view.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.Start)
    colors = []
    for _ in lines:
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
        colors.append(cursor.charFormat().foreground().color().name())
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

    expected = [
        QColor(Qt.GlobalColor.darkGray).name(),
        QColor(Qt.GlobalColor.black).name(),
        QColor(Qt.GlobalColor.darkYellow).name(),
        QColor(Qt.GlobalColor.red).name(),
        QColor(Qt.GlobalColor.magenta).name(),
    ]
    assert colors == expected
