import builtins
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from ..ui import create_button, CONTENT_MARGIN, DEFAULT_SPACING

# allow easy monkeypatching
open = builtins.open


class EnvTab(QWidget):
    """Edit the .env file of the current project."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(DEFAULT_SPACING)

        self.editor = QPlainTextEdit()
        layout.addWidget(self.editor)

        self.save_btn = create_button("Save")
        self.save_btn.clicked.connect(self.save_env)
        layout.addWidget(self.save_btn)

        self.load_env()

    def _env_path(self) -> Path:
        return Path(self.main_window.project_path) / ".env"

    def load_env(self) -> None:
        """Load the project's .env file into the editor."""
        self.editor.setPlainText("")
        path = self._env_path()
        if not self.main_window.project_path:
            return
        try:
            with open(str(path), "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
        except FileNotFoundError:
            # start with empty contents if file doesn't exist
            pass
        except OSError as e:
            print(f"Failed to read .env file: {e}")

    def save_env(self) -> None:
        """Write the editor contents back to the .env file."""
        if not self.main_window.project_path:
            return
        path = self._env_path()
        try:
            with open(str(path), "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
        except OSError as e:
            print(f"Failed to write .env file: {e}")
