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

    assert main.commands == [["npm", "install"]]


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


def test_dev_and_build_scripts_added(tmp_path, qtbot):
    pkg = {"scripts": {"dev": "vite", "build": "vite build"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = NodeTab(main)
    qtbot.addWidget(tab)
    tab.update_npm_scripts()

    texts = [btn.text() for btn in tab._script_buttons]
    assert texts.count("npm run dev") == 1
    assert texts.count("npm run build") == 1


def test_dev_and_build_buttons_run_commands(tmp_path, qtbot):
    pkg = {"scripts": {"dev": "vite", "build": "vite build"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = NodeTab(main)
    qtbot.addWidget(tab)
    tab.update_npm_scripts()

    dev_btn = next(btn for btn in tab._script_buttons if btn.text() == "npm run dev")
    build_btn = next(btn for btn in tab._script_buttons if btn.text() == "npm run build")
    qtbot.mouseClick(dev_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(build_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["npm", "run", "dev"], ["npm", "run", "build"]]
