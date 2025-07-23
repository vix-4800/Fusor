from PyQt6.QtCore import Qt
from fusor.tabs.makefile_tab import MakefileTab
import textwrap


class DummyMainWindow:
    def __init__(self):
        self.project_path = ""
        self.commands = []

    def run_command(self, cmd):
        self.commands.append(cmd)


def test_update_commands_adds_buttons(tmp_path, qtbot):
    makefile = textwrap.dedent(
        """
        build:
        @echo build

        test:
        @echo test
        """
    )
    (tmp_path / "Makefile").write_text(makefile)
    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = MakefileTab(main)
    qtbot.addWidget(tab)
    tab.update_commands()
    tab.show()
    qtbot.wait(10)
    texts = [btn.text() for btn in tab._buttons]
    assert "Build" in texts
    assert "Test" in texts
    assert tab.isVisible()


def test_command_button_runs_make(tmp_path, qtbot):
    (tmp_path / "Makefile").write_text("test:\n\t@echo test\n")
    main = DummyMainWindow()
    main.project_path = str(tmp_path)
    tab = MakefileTab(main)
    qtbot.addWidget(tab)
    tab.update_commands()
    btn = tab._buttons[0]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert main.commands == [["make", "test"]]

