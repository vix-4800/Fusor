from PyQt6.QtCore import Qt
from fusor.tabs.yii_tab import YiiTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []
        self.framework_choice = "Yii"

    def yii(self, *args):
        self.commands.append(list(args))


def test_buttons_run_commands(qtbot):
    main = DummyMainWindow()
    tab = YiiTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.cache_flush_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.migrate_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.make_migration_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [
        ["cache/flush-all"],
        ["migrate"],
        ["migrate/create"],
    ]


def test_visibility_changes(qtbot):
    main = DummyMainWindow()
    tab = YiiTab(main)
    qtbot.addWidget(tab)

    tab.on_framework_changed("None")
    assert tab.console_group.isHidden()

    tab.on_framework_changed("Yii")
    assert not tab.console_group.isHidden()

