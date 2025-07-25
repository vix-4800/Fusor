from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QCheckBox,
    QSizePolicy,
    QHBoxLayout,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QScrollArea,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from pathlib import Path, PurePath
from ..utils import expand_log_paths
from ..ui import create_button, BUTTON_SIZE, CONTENT_MARGIN, DEFAULT_SPACING


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
        outer_layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        outer_layout.setSpacing(16)

        # --- Log Selector ---
        self.log_selector = QComboBox()
        self.set_log_dirs(self.main_window.log_dirs)
        outer_layout.addWidget(self.log_selector)

        # --- Log Level Selector ---
        self.level_selector = QComboBox()
        self.level_selector.addItems([
            "All",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ])
        outer_layout.addWidget(self.level_selector)

        # --- Search ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(DEFAULT_SPACING)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search logs...")

        self.search_btn = create_button("", "edit-find", fixed=True)
        self.search_btn.clicked.connect(self.search_logs)

        self.prev_btn = create_button("", "go-previous", fixed=True)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(lambda: self.cycle_match(-1))

        self.next_btn = create_button("", "go-next", fixed=True)
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
        # Colorize logs when text changes
        self._colorizing = False
        self._level_colors = {
            "DEBUG": Qt.GlobalColor.darkGray,
            "INFO": Qt.GlobalColor.black,
            "WARNING": Qt.GlobalColor.darkYellow,
            "ERROR": Qt.GlobalColor.red,
            "CRITICAL": Qt.GlobalColor.magenta,
        }
        self.log_view.textChanged.connect(self._on_log_text_changed)
        outer_layout.addWidget(self.log_view)

        # --- Controls Group ---
        control_box = QGroupBox("Controls")
        self.control_box = control_box
        control_layout = QHBoxLayout()
        control_layout.setSpacing(DEFAULT_SPACING)

        refresh_btn = create_button("Refresh", "view-refresh")
        refresh_btn.clicked.connect(self.main_window.refresh_logs)
        control_layout.addWidget(refresh_btn)

        self.open_btn = create_button("Open File", "document-open")
        self.open_btn.clicked.connect(self.open_selected_log)
        control_layout.addWidget(self.open_btn)

        self.clear_btn = create_button("", "edit-clear", fixed=True)
        self.clear_btn.clicked.connect(self.main_window.clear_log_file)
        control_layout.addWidget(self.clear_btn)

        self.auto_checkbox = QCheckBox()
        self.auto_checkbox.setMinimumHeight(BUTTON_SIZE)
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

    def update_timer_interval(self, seconds: int) -> None:
        self._timer.setInterval(int(seconds) * 1000)
        self.auto_checkbox.setText(f"Auto refresh ({int(seconds)}s)")

    def set_log_dirs(self, paths: list[str]) -> None:
        self.log_selector.clear()
        expanded = expand_log_paths(self.main_window.project_path, paths)
        for p in expanded:
            self.log_selector.addItem(p, p)

    def on_auto_refresh_toggled(self, checked: bool) -> None:
        if checked:
            self._timer.start()
            self.main_window.refresh_logs()
        else:
            self._timer.stop()

    def search_logs(self) -> None:
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

    def _move_to_current_match(self, length: int) -> None:
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

    def cycle_match(self, delta: int) -> None:
        if not self._search_positions:
            return
        length = len(self.search_edit.text().strip())
        if length == 0:
            return
        self._current_search_index = (self._current_search_index + delta) % len(
            self._search_positions
        )
        self._move_to_current_match(length)

    def open_selected_log(self) -> None:
        """Open the currently selected log file with the system default app."""
        path = self.log_selector.currentData()
        if not path:
            return
        p = PurePath(path)
        if not p.is_absolute():
            p = Path(self.main_window.project_path) / p
        else:
            p = Path(p)
        self.main_window.open_file(str(p))

    def _on_log_text_changed(self) -> None:
        if self._colorizing:
            return
        self._colorizing = True
        try:
            text = self.log_view.toPlainText()
            cursor = self.log_view.textCursor()
            cursor.beginEditBlock()
            pos = 0
            for line in text.splitlines():
                fmt = QTextCharFormat()
                for lvl, color in self._level_colors.items():
                    if lvl in line:
                        fmt.setForeground(QColor(color))
                        break
                cursor.setPosition(pos)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    len(line),
                )
                cursor.mergeCharFormat(fmt)
                pos += len(line) + 1
            cursor.endEditBlock()
        finally:
            self._colorizing = False

    def update_responsive_layout(self, width: int) -> None:
        """Adjust layout visibility based on parent window width."""
        show_log = width >= 700
        self.log_view.setVisible(show_log)

        show_nav = width >= 600
        self.prev_btn.setVisible(show_nav)
        self.next_btn.setVisible(show_nav)

        if hasattr(self, "control_box"):
            self.control_box.setVisible(width >= 500)
