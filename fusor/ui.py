from PyQt6.QtWidgets import QPushButton, QSizePolicy
from typing import Optional

from .icons import get_icon

# Default UI constants
BUTTON_SIZE = 36
CONTENT_MARGIN = 20
DEFAULT_SPACING = 12


def create_button(
    text: str = "",
    icon: Optional[str] = None,
    *,
    fixed: bool = False,
    color: Optional[str] = None,
) -> QPushButton:
    """Return a QPushButton using the shared style constants.

    Parameters
    ----------
    text:
        Button label text.
    icon:
        Optional icon name from the theme.
    fixed:
        If ``True``, create a square button using ``BUTTON_SIZE``.
    color:
        Optional background color applied when the button is enabled.
    """
    btn = QPushButton(text)
    if icon:
        btn.setIcon(get_icon(icon))
    if fixed:
        btn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
    else:
        btn.setMinimumHeight(BUTTON_SIZE)
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    if color:
        btn.setStyleSheet(f"QPushButton:enabled {{ background-color: {color}; }}")
    return btn
