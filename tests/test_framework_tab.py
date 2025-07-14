from PyQt6.QtCore import Qt

from fusor.tabs.framework_tab import FrameworkTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        self.migrate = lambda: self.artisan("migrate")
        self.rollback = lambda: self.artisan("migrate:rollback")
        self.fresh = lambda: self.artisan("migrate:fresh")
        self.seed = lambda: self.artisan("db:seed")
        self.framework_choice = "Laravel"

    def run_command(self, cmd):
        self.commands.append(cmd)

    def artisan(self, *args):
        self.commands.append(list(args))


def test_artisan_buttons_run_commands(qtbot):
    main = DummyMainWindow()
    tab = FrameworkTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.optimize_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.config_clear_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["optimize"], ["config:clear"]]


def test_visibility_changes(qtbot):
    main = DummyMainWindow()
    tab = FrameworkTab(main)
    qtbot.addWidget(tab)

    tab.on_framework_changed("None")
    assert tab.artisan_group.isHidden()
    assert tab.migrate_group.isHidden()

    tab.on_framework_changed("Laravel")
    assert not tab.artisan_group.isHidden()
    assert not tab.migrate_group.isHidden()
