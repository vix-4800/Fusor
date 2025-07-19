from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
)
import logging

logger = logging.getLogger(__name__)


class BranchDialog(QDialog):
    """Dialog listing branches for selection."""

    def __init__(self, branches: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Branch")
        layout = QVBoxLayout(self)

        self.branches = list(branches)

        layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.update_filter)
        layout.addWidget(self.search_edit)

        layout.addWidget(QLabel("Branch:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.update_filter("")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.list_widget.itemDoubleClicked.connect(lambda *_: self.accept())

    def update_filter(self, text: str):
        self.list_widget.clear()
        text = text.lower()
        for branch in self.branches:
            if text in branch.lower():
                self.list_widget.addItem(branch)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def get_branch(self) -> str:
        item = self.list_widget.currentItem()
        return item.text() if item else ""
