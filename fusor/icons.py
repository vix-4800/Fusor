from PyQt6.QtGui import QIcon


def get_icon(name: str) -> QIcon:
    """Return a themed QIcon or an empty icon if unavailable."""
    icon = QIcon.fromTheme(name)
    return icon if not icon.isNull() else QIcon()
