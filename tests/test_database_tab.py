from PyQt6.QtCore import Qt

from fusor.tabs.database_tab import DatabaseTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        self.framework_choice = "Laravel"
        self.db_service = "db"

    # stubs used by buttons but not tested here
    migrate = rollback = fresh = seed = lambda self: None

    def run_command(self, cmd, service=None):
        self.commands.append((cmd, service))


def test_dbeaver_button_runs_command(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.dbeaver_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [(["dbeaver"], "db")]


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

    assert main.commands == [(["mysqldump", "--result-file", "/tmp/d.sql"], "db")]


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

    assert main.commands == [(["mysql", "/tmp/d.sql"], "db")]


def test_postgres_dump_and_restore(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    tab.db_combo.setCurrentText("PostgreSQL")

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/tmp/p.sql", ""),
        raising=True,
    )
    qtbot.mouseClick(tab.dump_btn, Qt.MouseButton.LeftButton)

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getOpenFileName",
        lambda *a, **k: ("/tmp/p.sql", ""),
        raising=True,
    )
    qtbot.mouseClick(tab.restore_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [
        (["pg_dump", "-f", "/tmp/p.sql"], "db"),
        (["psql", "-f", "/tmp/p.sql"], "db"),
    ]


def test_service_name_passed(monkeypatch, qtbot):
    main = DummyMainWindow()
    main.db_service = "maria"
    tab = DatabaseTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(
        "PyQt6.QtWidgets.QFileDialog.getSaveFileName",
        lambda *a, **k: ("/tmp/d.sql", ""),
        raising=True,
    )

    qtbot.mouseClick(tab.dump_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [(["mysqldump", "--result-file", "/tmp/d.sql"], "maria")]


