import subprocess
from PyQt6.QtWidgets import QMessageBox

from fusor.tabs.git_tab import GitTab


class DummyMainWindow:
    def __init__(self, path="/repo"):
        self.project_path = path
        self.ensure_called = 0

    def ensure_project_path(self):
        self.ensure_called += 1
        return bool(self.project_path)

    git_remote = "origin"


def test_load_branches_and_run_git_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    results = {}

    class DummyResult:
        def __init__(self, stdout="", returncode=0):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = returncode

    def fake_run(cmd, capture_output=True, text=True, cwd=None):
        assert cwd == main.project_path
        if cmd[:3] == ["git", "branch", "--format=%(refname:short)"]:
            res = DummyResult("main\ndevelop\n")
        elif cmd[:2] == ["git", "rev-parse"]:
            res = DummyResult("main")
        else:
            res = DummyResult("status")
        results[tuple(cmd)] = res
        return res

    monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

    tab.load_branches()
    assert [tab.branch_combo.itemText(i) for i in range(tab.branch_combo.count())] == [
        "main",
        "develop",
    ]
    assert tab.current_branch == "main"

    res = tab.run_git_command("status")
    assert res is results[("git", "status")]


def test_on_branch_changed_triggers_checkout(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)
    tab.current_branch = "main"

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
        raising=True,
    )

    called = {}

    def fake_run_git_command(*args):
        called["args"] = args

    monkeypatch.setattr(tab, "run_git_command", fake_run_git_command, raising=True)

    tab.on_branch_changed("develop")

    assert called["args"] == ("checkout", "develop")
    assert tab.current_branch == "develop"


def test_hard_reset_runs_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
        raising=True,
    )

    called = {}

    class DummyResult:
        def __init__(self, returncode=0):
            self.stdout = ""
            self.stderr = ""
            self.returncode = returncode

    def fake_run_git_command(*args):
        called["args"] = args
        return DummyResult()

    monkeypatch.setattr(tab, "run_git_command", fake_run_git_command, raising=True)

    tab.hard_reset()

    assert called["args"] == ("reset", "--hard")


def test_remote_helpers(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    class DummyResult:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    outputs = {
        ("git", "remote"): DummyResult("origin\nupstream\n"),
        ("git", "ls-remote", "--heads", "origin"): DummyResult("sha\trefs/heads/main\nsha\trefs/heads/feature\n"),
    }

    def fake_run(cmd, capture_output=True, text=True, cwd=None):
        assert cwd == main.project_path
        return outputs[tuple(cmd)]

    monkeypatch.setattr(subprocess, "run", fake_run, raising=True)

    assert tab.get_remotes() == ["origin", "upstream"]
    tab.load_remote_branches()
    assert [tab.remote_branch_combo.itemText(i) for i in range(tab.remote_branch_combo.count())] == [
        "main",
        "feature",
    ]
