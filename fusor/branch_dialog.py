from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel


class BranchDialog(QDialog):
    """Dialog listing branches for selection."""

    def __init__(self, branches: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Branch")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Branch:"))
        self.list_widget = QListWidget()
        self.list_widget.addItems(branches)
        if branches:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.list_widget.itemDoubleClicked.connect(lambda *_: self.accept())

    def get_branch(self) -> str:
        item = self.list_widget.currentItem()
        return item.text() if item else ""
