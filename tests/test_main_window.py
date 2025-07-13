import builtins
import os
from PyQt6.QtWidgets import QApplication
import fusor.main_window as mw_module
from fusor.main_window import MainWindow

class DummyLogView:
    def __init__(self):
        self.text = None
    def setPlainText(self, text):
        self.text = text

def test_refresh_logs_no_project_path(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # prevent dialog on construction
    monkeypatch.setattr(mw_module.QTimer, "singleShot", lambda *a, **k: None)
    monkeypatch.setattr(MainWindow, "ask_project_path", lambda self: None)
    # avoid reading real config
    monkeypatch.setattr(mw_module, "load_config", lambda: {})

    window = MainWindow()
    window.project_path = ""
    dummy = DummyLogView()
    window.log_view = dummy
    close_called = []
    monkeypatch.setattr(window, "close", lambda: close_called.append(True))

    def fail(*args, **kwargs):
        raise AssertionError("log access attempted")

    monkeypatch.setattr(os.path, "exists", fail)
    monkeypatch.setattr(builtins, "open", fail)

    window.refresh_logs()

    assert close_called == [True]
    assert dummy.text is None
