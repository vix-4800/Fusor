from PyQt6.QtCore import Qt

from fusor.tabs.database_tab import DatabaseTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        self.framework_choice = "Laravel"

    # stubs used by buttons but not tested here
    migrate = rollback = fresh = seed = lambda self: None

    def run_command(self, cmd):
        self.commands.append(cmd)


def test_dbeaver_button_runs_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.dbeaver_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["dbeaver"]]


def test_dump_button_runs_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/tmp/d.sql", ""),
        raising=True,
    )

    qtbot.mouseClick(tab.dump_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["mysqldump", "--result-file", "/tmp/d.sql"]]


def test_restore_button_runs_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getOpenFileName",
        lambda *a, **k: ("/tmp/d.sql", ""),
        raising=True,
    )

    qtbot.mouseClick(tab.restore_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["mysql", "/tmp/d.sql"]]


