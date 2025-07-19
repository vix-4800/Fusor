import json
from PyQt6.QtCore import Qt

from fusor.tabs.node_tab import NodeTab


class DummyMainWindow:
    def __init__(self):
        self.project_path = ""
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


def test_update_npm_scripts_adds_buttons(tmp_path, qtbot):
    pkg = {"scripts": {"start": "node index.js"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = NodeTab(main)
    qtbot.addWidget(tab)
    tab.update_npm_scripts()
    tab.show()
    qtbot.wait(10)

    texts = [btn.text() for btn in tab._script_buttons]
    assert "npm run start" in texts
    assert tab.npm_scripts_group.isVisible()


def test_script_button_runs_command(tmp_path, qtbot, monkeypatch):
    pkg = {"scripts": {"start": "node index.js"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    captured = []
    monkeypatch.setattr(main, "run_command", lambda cmd: captured.append(cmd), raising=True)
    tab = NodeTab(main)
    qtbot.addWidget(tab)
    tab.update_npm_scripts()
    btn = tab._script_buttons[0]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    assert captured == [["npm", "run", "start"]]
