import subprocess
from PyQt6.QtWidgets import QMessageBox, QPushButton, QDialog
from PyQt6.QtCore import Qt

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


def test_push_button_runs_push(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    called = {}

    def fake_run_git_command(*args):
        called["args"] = args

    monkeypatch.setattr(tab, "run_git_command", fake_run_git_command, raising=True)

    push_btn: QPushButton | None = None
    for btn in tab.findChildren(QPushButton):
        if btn.text() == "Push":
            push_btn = btn
            break
    assert push_btn is not None

    qtbot.mouseClick(push_btn, Qt.MouseButton.LeftButton)

    assert called["args"] == ("push",)


def test_create_branch_button(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    called = {}

    def fake_run_git_command(*args):
        called["args"] = args

    monkeypatch.setattr(tab, "run_git_command", fake_run_git_command, raising=True)

    create_btn: QPushButton | None = None
    for btn in tab.findChildren(QPushButton):
        if btn.text() == "Create Branch":
            create_btn = btn
            break
    assert create_btn is not None

    tab.branch_name_edit.setText("feature")
    qtbot.mouseClick(create_btn, Qt.MouseButton.LeftButton)

    assert called["args"] == ("checkout", "-b", "feature")


def test_view_log_button_runs_log(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    called = {}

    def fake_run_git_command(*args):
        called["args"] = args

    monkeypatch.setattr(tab, "run_git_command", fake_run_git_command, raising=True)

    view_btn: QPushButton | None = None
    for btn in tab.findChildren(QPushButton):
        if btn.text() == "View Log":
            view_btn = btn
            break
    assert view_btn is not None

    qtbot.mouseClick(view_btn, Qt.MouseButton.LeftButton)

    assert called["args"] == ("log", "-n", "20", "--oneline")


def test_branch_dialog_get_branch(qtbot):
    from fusor.branch_dialog import BranchDialog

    dialog = BranchDialog(["main", "dev"])
    qtbot.addWidget(dialog)
    dialog.list_widget.setCurrentRow(1)
    assert dialog.get_branch() == "dev"


def test_show_branch_dialog_checks_out(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = GitTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(tab, "fetch_local_branches", lambda: ["main"], raising=True)
    monkeypatch.setattr(tab, "fetch_remote_branches", lambda: ["feature"], raising=True)

    called = {}
    monkeypatch.setattr(tab, "checkout_remote_branch", lambda b: called.setdefault("remote", b), raising=True)
    monkeypatch.setattr(tab, "checkout", lambda b: called.setdefault("local", b), raising=True)

    class DummyDialog:
        def __init__(self, branches, parent=None):
            self.branches = branches
        def exec(self):
            return QDialog.DialogCode.Accepted
        def get_branch(self):
            return "origin/feature"

    monkeypatch.setattr("fusor.tabs.git_tab.BranchDialog", DummyDialog, raising=True)

    tab.show_branch_dialog()

    assert called.get("remote") == "feature"
