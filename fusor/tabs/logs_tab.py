from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QSizePolicy,
    QHBoxLayout,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QScrollArea,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor
from ..icons import get_icon
import logging

logger = logging.getLogger(__name__)


class LogsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # search state
        self._search_positions: list[int] = []
        self._current_search_index = 0

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(16)

        # --- Log Selector ---
        self.log_selector = QComboBox()
        self.set_log_paths(self.main_window.log_paths)
        outer_layout.addWidget(self.log_selector)

        # --- Search ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search logs...")

        self.search_btn = QPushButton("Search")
        self.search_btn.setIcon(get_icon("edit-find"))
        self.search_btn.setMinimumHeight(36)
        self.search_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.search_btn.clicked.connect(self.search_logs)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setIcon(get_icon("go-previous"))
        self.prev_btn.setMinimumHeight(36)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(lambda: self.cycle_match(-1))

        self.next_btn = QPushButton("Next")
        self.next_btn.setIcon(get_icon("go-next"))
        self.next_btn.setMinimumHeight(36)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(lambda: self.cycle_match(1))

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.prev_btn)
        search_layout.addWidget(self.next_btn)
        outer_layout.addLayout(search_layout)

        # --- Log Output ---
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("No logs loaded yet...")
        self.log_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        outer_layout.addWidget(self.log_view)

        # --- Controls Group ---
        control_box = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(get_icon("view-refresh"))
        refresh_btn.setMinimumHeight(36)
        refresh_btn.clicked.connect(self.main_window.refresh_logs)
        refresh_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        control_layout.addWidget(refresh_btn)

        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.setIcon(get_icon("edit-clear"))
        self.clear_btn.setMinimumHeight(36)
        self.clear_btn.clicked.connect(self.main_window.clear_log_file)
        self.clear_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        control_layout.addWidget(self.clear_btn)

        self.auto_checkbox = QCheckBox()
        self.auto_checkbox.setMinimumHeight(36)
        self.auto_checkbox.setChecked(False)
        control_layout.addWidget(
            self.auto_checkbox, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        control_box.setLayout(control_layout)
        outer_layout.addWidget(control_box)

        outer_layout.addStretch(1)

        # Expose log view to main_window
        self.main_window.log_view = self.log_view

        # Timer for auto-refresh
        self._timer = QTimer(self)
        self.update_timer_interval(self.main_window.auto_refresh_secs)
        self._timer.timeout.connect(self.main_window.refresh_logs)
        self.auto_checkbox.toggled.connect(self.on_auto_refresh_toggled)

    def update_timer_interval(self, seconds: int):
        self._timer.setInterval(int(seconds) * 1000)
        self.auto_checkbox.setText(f"Auto refresh ({int(seconds)}s)")

    def set_log_paths(self, paths: list[str]) -> None:
        self.log_selector.clear()
        self.log_selector.addItem("All logs", None)
        for p in paths:
            self.log_selector.addItem(p, p)

    def on_auto_refresh_toggled(self, checked: bool):
        if checked:
            self._timer.start()
            self.main_window.refresh_logs()
        else:
            self._timer.stop()

    def search_logs(self):
        text = self.search_edit.text().strip()
        if not text:
            self.log_view.setExtraSelections([])
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return

        content = self.log_view.toPlainText()
        text_lower = text.lower()

        # Find all match positions
        self._search_positions.clear()
        start = 0
        while True:
            idx = content.lower().find(text_lower, start)
            if idx == -1:
                break
            self._search_positions.append(idx)
            start = idx + len(text)

        if not self._search_positions:
            self.log_view.setExtraSelections([])
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return

        # Highlight all matches
        selections = []
        for pos in self._search_positions:
            cursor = self.log_view.textCursor()
            cursor.setPosition(pos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(text),
            )
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(Qt.GlobalColor.yellow)
            selections.append(selection)
        self.log_view.setExtraSelections(selections)

        self._current_search_index = 0
        self.prev_btn.setEnabled(len(self._search_positions) > 1)
        self.next_btn.setEnabled(len(self._search_positions) > 1)
        self._move_to_current_match(len(text))

    def _move_to_current_match(self, length: int):
        if not self._search_positions:
            return
        pos = self._search_positions[self._current_search_index]
        cursor = self.log_view.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            length,
        )
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def cycle_match(self, delta: int):
        if not self._search_positions:
            return
        length = len(self.search_edit.text().strip())
        if length == 0:
            return
        self._current_search_index = (self._current_search_index + delta) % len(
            self._search_positions
        )
        self._move_to_current_match(length)
