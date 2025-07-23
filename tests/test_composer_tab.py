import json
from PyQt6.QtCore import Qt


from fusor.tabs.composer_tab import ComposerTab


class DummyMainWindow:
    def __init__(self):
        self.project_path = ""
        self.commands = []

    def run_command(self, cmd):
        self.commands.append(cmd)


def test_buttons_run_commands(qtbot):
    main = DummyMainWindow()
    tab = ComposerTab(main)
    qtbot.addWidget(tab)

    qtbot.mouseClick(tab.install_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(tab.update_btn, Qt.MouseButton.LeftButton)

    assert main.commands == [["composer", "install"], ["composer", "update"]]


def test_update_composer_scripts_adds_buttons(tmp_path, qtbot):
    data = {"scripts": {"lint": "phpcs"}}
    (tmp_path / "composer.json").write_text(json.dumps(data))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = ComposerTab(main)
    qtbot.addWidget(tab)
    tab.update_composer_scripts()
    tab.show()
    qtbot.wait(10)

    texts = [btn.text() for btn in tab._script_buttons]
    assert "Lint" in texts
    assert tab.scripts_group.isVisible()


def test_script_button_runs_command(tmp_path, qtbot, monkeypatch):
    data = {"scripts": {"lint": "phpcs"}}
    (tmp_path / "composer.json").write_text(json.dumps(data))

    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    captured = []
    monkeypatch.setattr(main, "run_command", lambda cmd: captured.append(cmd), raising=True)
    tab = ComposerTab(main)
    qtbot.addWidget(tab)
    tab.update_composer_scripts()
    btn = tab._script_buttons[0]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    assert captured == [["composer", "run", "lint"]]
