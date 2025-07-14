from PyQt6.QtCore import Qt

from fusor.tabs.database_tab import DatabaseTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        # stubs used by migration buttons but not tested here
        self.migrate = lambda: None
        self.rollback = lambda: None
        self.fresh = lambda: None
        self.seed = lambda: None
        self.framework_choice = "Laravel"

    def run_command(self, cmd):
        self.commands.append(cmd)

    def artisan(self, *args):
        self.commands.append(list(args))


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


def test_optimize_button_runs_command(qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.optimize_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["optimize"]]


def test_config_clear_button_runs_command(qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.config_clear_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["config:clear"]]


def test_artisan_group_visibility_changes(qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    tab.on_framework_changed("None")
    assert tab.artisan_group.isHidden()
    assert tab.migrate_group.isHidden()

    tab.on_framework_changed("Laravel")
    assert not tab.artisan_group.isHidden()
    assert not tab.migrate_group.isHidden()
