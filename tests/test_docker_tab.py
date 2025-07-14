from PyQt6.QtCore import Qt

from fusor.tabs.docker_tab import DockerTab


class DummyMainWindow:
    def __init__(self):
        self.commands = []

    def run_command(self, cmd):
        self.commands.append(cmd)


def test_buttons_run_commands(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = DockerTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.build_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.pull_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.status_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.logs_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.restart_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [
        ["docker", "compose", "build"],
        ["docker", "compose", "pull"],
        ["docker", "compose", "ps"],
        ["docker", "compose", "logs", "--tail", "50"],
        ["docker", "compose", "restart"],
    ]
