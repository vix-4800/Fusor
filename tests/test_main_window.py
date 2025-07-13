import os
import subprocess
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt6.QtWidgets import QApplication
from fusor.main_window import MainWindow


def test_start_project_uses_configured_php(tmp_path, monkeypatch):
    # ensure QApplication exists for MainWindow
    app = QApplication.instance() or QApplication([])

    window = MainWindow()
    window.project_path = str(tmp_path)
    window.framework_choice = "None"
    if hasattr(window, "framework_combo"):
        window.framework_combo.setCurrentText("None")
    window.php_path = "/custom/php"

    (tmp_path / "public").mkdir()

    called = {}

    class DummyProcess:
        def __init__(self):
            self.stdout = []

        def poll(self):
            return None

    def fake_popen(cmd, **kwargs):
        called["cmd"] = cmd
        return DummyProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(window.executor, "submit", lambda fn: None)

    window.start_project()

    assert called["cmd"][0] == "/custom/php"

    app.quit()
