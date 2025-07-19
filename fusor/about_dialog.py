from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtCore import Qt
import logging
from . import APP_NAME, __version__, DESCRIPTION, AUTHOR

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    """Simple dialog showing project information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        layout = QVBoxLayout(self)

        title = QLabel(f"<h2>{APP_NAME}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel(f"Version: {__version__}"))
        layout.addWidget(QLabel(f"Author: {AUTHOR}"))
        layout.addWidget(QLabel(DESCRIPTION))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignCenter)
