from __future__ import annotations

import os
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QLineEdit,
    QPushButton,
)


class TerminalTab(QWidget):
    """Simple embedded terminal using QProcess."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.process: QProcess | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setEnabled(False)
        self.input_edit.returnPressed.connect(self.send_input)
        input_layout.addWidget(self.input_edit)
        self.send_btn = QPushButton("Send")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Shell")
        self.start_btn.clicked.connect(self.start_shell)
        btn_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(
            "QPushButton:enabled { background-color: #dc3545; }"
        )
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_shell)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _shell_program(self) -> str:
        if os.name == "nt":
            return "cmd.exe"
        return os.environ.get("SHELL", "/bin/sh")

    def _handle_output(self) -> None:
        if not self.process:
            return
        out = bytes(self.process.readAllStandardOutput().data()).decode(
            errors="ignore"
        )
        err = bytes(self.process.readAllStandardError().data()).decode(
            errors="ignore"
        )
        text = out + err
        if text:
            self.output.appendPlainText(text.rstrip())

    # ------------------------------------------------------------------
    # actions
    # ------------------------------------------------------------------
    def start_shell(self) -> None:
        if (
            self.process is not None
            and self.process.state() == QProcess.ProcessState.Running
        ):
            return
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_output)
        self.process.readyReadStandardError.connect(self._handle_output)
        self.process.finished.connect(self._on_finished)
        program = self._shell_program()
        if self.main_window.project_path:
            self.process.setWorkingDirectory(self.main_window.project_path)
        self.process.start(program)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.send_btn.setEnabled(True)

    def _on_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.process = None

    def stop_shell(self) -> None:
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.process = None
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.input_edit.setEnabled(False)
            self.send_btn.setEnabled(False)

    def send_input(self) -> None:
        if not self.process or self.process.state() != QProcess.ProcessState.Running:
            return
        text = self.input_edit.text()
        if not text:
            return
        self.process.write((text + "\n").encode())
        self.output.appendPlainText(f"$ {text}")
        self.input_edit.clear()
