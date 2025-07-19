from PyQt6.QtCore import Qt

from fusor.tabs.node_tab import NodeTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []

    def run_command(self, cmd):
        self.commands.append(cmd)


def test_buttons_run_commands(qtbot):
    main = DummyMainWindow()
    tab = NodeTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.npm_install_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.npm_dev_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.npm_build_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [
        ["npm", "install"],
        ["npm", "run", "dev"],
        ["npm", "run", "build"],
    ]
