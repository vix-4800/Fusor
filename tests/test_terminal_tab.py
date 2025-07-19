from PyQt6.QtCore import QProcess
from fusor.tabs.terminal_tab import TerminalTab

class DummyMainWindow:
    def __init__(self):
        self.project_path = "/proj"

def test_start_and_stop_shell(monkeypatch, qtbot):
    main = DummyMainWindow()
    tab = TerminalTab(main)
    qtbot.addWidget(tab)

    assert not tab.input_edit.isEnabled()
    assert not tab.send_btn.isEnabled()

    started = []
    killed = []

    class DummyProc:
        ProcessState = QProcess.ProcessState

        def __init__(self, *args, **kwargs):
            self._state = QProcess.ProcessState.NotRunning
            self.readyReadStandardOutput = type("Sig", (), {"connect": lambda *a, **k: None})()
            self.readyReadStandardError = type("Sig", (), {"connect": lambda *a, **k: None})()
            self.finished = type("Sig", (), {"connect": lambda *a, **k: None})()
        def start(self, program):
            started.append(program)
            self._state = QProcess.ProcessState.Running
        def state(self):
            return self._state
        def kill(self):
            killed.append(True)
            self._state = QProcess.ProcessState.NotRunning
        def write(self, *_a):
            pass
        def setWorkingDirectory(self, *_a):
            pass
    monkeypatch.setattr("fusor.tabs.terminal_tab.QProcess", DummyProc)

    tab.start_shell()
    assert started
    assert not tab.start_btn.isEnabled()
    assert tab.stop_btn.isEnabled()
    assert tab.input_edit.isEnabled()
    assert tab.send_btn.isEnabled()

    tab.stop_shell()
    assert killed
    assert tab.start_btn.isEnabled()
    assert not tab.stop_btn.isEnabled()
    assert not tab.input_edit.isEnabled()
    assert not tab.send_btn.isEnabled()
