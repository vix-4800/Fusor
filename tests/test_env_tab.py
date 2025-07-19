from pathlib import Path
from fusor.tabs.env_tab import EnvTab
import fusor.tabs.env_tab as env_module

class DummyMainWindow:
    def __init__(self, path: str):
        self.project_path = path


def test_load_edit_save(tmp_path, qtbot, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=1")

    opened = []
    real_open = env_module.open

    def fake_open(path, mode="r", *args, **kwargs):
        opened.append((path, mode))
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(env_module, "open", fake_open, raising=True)

    main = DummyMainWindow(str(tmp_path))
    tab = EnvTab(main)
    qtbot.addWidget(tab)

    assert opened[0] == (str(env_file), "r")
    assert tab.editor.toPlainText() == "FOO=1"

    tab.editor.setPlainText("FOO=2")
    tab.save_env()

    assert opened[1] == (str(env_file), "w")
    assert env_file.read_text() == "FOO=2"

