from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from ..icons import get_icon

class DockerTab(QWidget):
    """Additional Docker helper commands."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.build_btn = self._btn(
            "🔨 Rebuild Images", self.build, icon="system-run"
        )
        self.pull_btn = self._btn(
            "⬇ Pull Images", self.pull, icon="go-down"
        )
        self.status_btn = self._btn(
            "📋 Status", self.status, icon="dialog-information"
        )
        self.logs_btn = self._btn(
            "📄 Logs", self.logs, icon="text-x-generic"
        )
        self.restart_btn = self._btn(
            "🔄 Restart", self.restart, icon="view-refresh"
        )

        layout.addWidget(self.build_btn)
        layout.addWidget(self.pull_btn)
        layout.addWidget(self.status_btn)
        layout.addWidget(self.logs_btn)
        layout.addWidget(self.restart_btn)

        layout.addStretch(1)

    def _btn(self, text, slot, icon: str | None = None):
        btn = QPushButton(text)
        if icon:
            btn.setIcon(get_icon(icon))
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
