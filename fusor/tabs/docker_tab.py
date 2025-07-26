from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from ..ui import create_button, CONTENT_MARGIN, DEFAULT_SPACING


class DockerTab(QWidget):
    """Additional Docker helper commands."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(DEFAULT_SPACING)

        self.build_btn = create_button("Rebuild Images", "system-run")
        self.build_btn.clicked.connect(self.build)
        self.pull_btn = create_button("Pull Images", "go-down")
        self.pull_btn.clicked.connect(self.pull)
        self.status_btn = create_button("Status", "dialog-information")
        self.status_btn.clicked.connect(self.status)
        self.logs_btn = create_button("Logs", "text-x-generic")
        self.logs_btn.clicked.connect(self.logs)
        self.restart_btn = create_button("Restart", "view-refresh")
        self.restart_btn.clicked.connect(self.restart)
        self.shell_btn = create_button("Open Shell", "utilities-terminal")
        self.shell_btn.clicked.connect(self.shell)

        layout.addWidget(self.build_btn)
        layout.addWidget(self.pull_btn)
        layout.addWidget(self.status_btn)
        layout.addWidget(self.logs_btn)
        layout.addWidget(self.restart_btn)
        layout.addWidget(self.shell_btn)

        layout.addStretch(1)

    def build(self) -> None:
        self.main_window.run_command(["docker", "compose", "build"])

    def pull(self) -> None:
        self.main_window.run_command(["docker", "compose", "pull"])

    def status(self) -> None:
        self.main_window.run_command(["docker", "compose", "ps"])

    def logs(self) -> None:
        self.main_window.run_command(["docker", "compose", "logs", "--tail", "50"])

    def restart(self) -> None:
        self.main_window.run_command(["docker", "compose", "restart"])

    def shell(self) -> None:
        self.main_window.run_command(
            ["docker", "compose", "exec", self.main_window.php_service, "sh"]
        )
