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

        def start(self, program, args=None):
            started.append([program] + (args or []))
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


def test_start_shell_docker_exec(monkeypatch, qtbot):
    class DockerMain(DummyMainWindow):
        def __init__(self):
            super().__init__()
            self.use_docker = True
            self.php_service = "php"

        def _compose_prefix(self):
            return ["docker", "compose"]

    main = DockerMain()
    tab = TerminalTab(main)
    qtbot.addWidget(tab)

    monkeypatch.setattr(TerminalTab, "_shell_program", lambda self: "/bin/sh")

    started = []
    cwd_set = []

    class DummyProc:
        ProcessState = QProcess.ProcessState

        def __init__(self, *args, **kwargs):
            self._state = QProcess.ProcessState.NotRunning
            self.readyReadStandardOutput = type("Sig", (), {"connect": lambda *a, **k: None})()
            self.readyReadStandardError = type("Sig", (), {"connect": lambda *a, **k: None})()
            self.finished = type("Sig", (), {"connect": lambda *a, **k: None})()

        def start(self, program, args=None):
            started.append([program] + (args or []))
            self._state = QProcess.ProcessState.Running

        def state(self):
            return self._state

        def kill(self):
            self._state = QProcess.ProcessState.NotRunning

        def write(self, *_a):
            pass

        def setWorkingDirectory(self, path):
            cwd_set.append(path)

    monkeypatch.setattr("fusor.tabs.terminal_tab.QProcess", DummyProc)

    tab.start_shell()

    assert cwd_set == ["/proj"]
    assert started[0] == [
        "docker",
        "compose",
        "exec",
        "-T",
        "-w",
        "/proj",
        "php",
        "/bin/sh",
    ]
