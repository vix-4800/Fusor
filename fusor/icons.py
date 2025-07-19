from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt


def get_icon(name: str) -> QIcon:
    """Return a themed QIcon or an empty icon if unavailable."""
    icon = QIcon.fromTheme(name)
    return icon if not icon.isNull() else QIcon()


def get_notification_icon() -> QIcon:
    """Return a non-null icon for tray notifications."""
    icon = QIcon.fromTheme("dialog-information")
    if icon.isNull():
        px = QPixmap(1, 1)
        px.fill(Qt.GlobalColor.transparent)
        icon = QIcon(px)
    return icon

