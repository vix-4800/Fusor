from PyQt6.QtCore import Qt

from fusor.tabs.symfony_tab import SymfonyTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        self.framework_choice = "Symfony"

    def symfony(self, *args):
        self.commands.append(list(args))


def test_buttons_run_commands(qtbot):
    main = DummyMainWindow()
    tab = SymfonyTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.cache_clear_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.migrate_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.status_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.make_migration_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [
        ["cache:clear"],
        ["doctrine:migrations:migrate"],
        ["doctrine:migrations:status"],
        ["make:migration"],
    ]


def test_visibility_changes(qtbot):
    main = DummyMainWindow()
    tab = SymfonyTab(main)
    qtbot.addWidget(tab)

    tab.on_framework_changed("None")
    assert tab.console_group.isHidden()

    tab.on_framework_changed("Symfony")
    assert not tab.console_group.isHidden()

