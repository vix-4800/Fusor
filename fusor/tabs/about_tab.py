from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from .. import APP_NAME, __version__, DESCRIPTION, AUTHOR
from ..ui import CONTENT_MARGIN, DEFAULT_SPACING


class AboutTab(QWidget):
    """Display basic application information."""

    def __init__(self, main_window):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(DEFAULT_SPACING)

        title = QLabel(f"<h2>{APP_NAME}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel(f"Version: {__version__}"))
        layout.addWidget(QLabel(f"Author: {AUTHOR}"))
        layout.addWidget(QLabel(DESCRIPTION))
        layout.addStretch(1)
