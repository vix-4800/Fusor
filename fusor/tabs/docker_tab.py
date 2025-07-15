from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class DockerTab(QWidget):
    """Additional Docker helper commands."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.build_btn = self._btn("🔨 Rebuild Images", self.build)
        self.pull_btn = self._btn("⬇ Pull Images", self.pull)
        self.status_btn = self._btn("📋 Status", self.status)
        self.logs_btn = self._btn("📄 Logs", self.logs)
        self.restart_btn = self._btn("🔄 Restart", self.restart)

        layout.addWidget(self.build_btn)
        layout.addWidget(self.pull_btn)
        layout.addWidget(self.status_btn)
        layout.addWidget(self.logs_btn)
        layout.addWidget(self.restart_btn)

        layout.addStretch(1)

    def _btn(self, text, slot):
        btn = QPushButton(text)
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def build(self):
        self.main_window.run_command(["docker", "compose", "build"])

    def pull(self):
        self.main_window.run_command(["docker", "compose", "pull"])

    def status(self):
        self.main_window.run_command(["docker", "compose", "ps"])

    def logs(self):
        self.main_window.run_command(["docker", "compose", "logs", "--tail", "50"])

    def restart(self):
        self.main_window.run_command(["docker", "compose", "restart"])
