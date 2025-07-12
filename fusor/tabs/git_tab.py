from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QSizePolicy


class GitTab(QWidget):
    """Tab providing basic Git actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems(["main", "dev", "feature/example"])
        self.branch_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.branch_combo)

        checkout_btn = QPushButton("Checkout")
        checkout_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        checkout_btn.clicked.connect(self.checkout)
        layout.addWidget(checkout_btn)

        pull_btn = QPushButton("Pull")
        pull_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pull_btn.clicked.connect(lambda: print("Pull clicked"))
        layout.addWidget(pull_btn)

        hard_reset_btn = QPushButton("Hard reset")
        hard_reset_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hard_reset_btn.clicked.connect(lambda: print("Hard reset clicked"))
        layout.addWidget(hard_reset_btn)

        stash_btn = QPushButton("Stash")
        stash_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stash_btn.clicked.connect(lambda: print("Stash clicked"))
        layout.addWidget(stash_btn)

    def checkout(self):
        print(f"Checkout {self.branch_combo.currentText()}")
