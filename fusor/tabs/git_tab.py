from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QSizePolicy,
    QMessageBox,
)
import subprocess

class GitTab(QWidget):
    """Tab providing basic Git actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.branch_combo = QComboBox()
        self.branch_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.branch_combo)

        self.current_branch = ""
        self.load_branches()
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)

        pull_btn = QPushButton("Pull")
        pull_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pull_btn.clicked.connect(lambda: self.run_git_command("pull"))
        layout.addWidget(pull_btn)

        hard_reset_btn = QPushButton("Hard reset")
        hard_reset_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hard_reset_btn.clicked.connect(lambda: print("Hard reset clicked"))
        layout.addWidget(hard_reset_btn)

        stash_btn = QPushButton("Stash")
        stash_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stash_btn.clicked.connect(lambda: print("Stash clicked"))
        layout.addWidget(stash_btn)

    def run_git_command(self, *args):
        self.main_window.ensure_project_path()
        command = ["git", *args]
        print(f"$ {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip())
        except FileNotFoundError:
            print("Command not found: git")

    def load_branches(self):
        self.main_window.ensure_project_path()
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            branches = [b.strip() for b in result.stdout.splitlines() if b.strip()]
            self.branch_combo.blockSignals(True)
            self.branch_combo.clear()
            self.branch_combo.addItems(branches)

            head = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            current = head.stdout.strip()
            if current in branches:
                self.branch_combo.setCurrentText(current)
            self.current_branch = current
            self.branch_combo.blockSignals(False)
        except FileNotFoundError:
            print("Command not found: git")

    def checkout(self, branch):
        self.main_window.ensure_project_path()
        self.run_git_command("checkout", branch)
        self.current_branch = branch

    def on_branch_changed(self, branch):
        if not branch or branch == self.current_branch:
            return
        self.main_window.ensure_project_path()
        reply = QMessageBox.question(
            self,
            "Checkout Branch",
            f"Switch to branch '{branch}'?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.checkout(branch)
        else:
            # revert selection to previous branch
            self.branch_combo.blockSignals(True)
            self.branch_combo.setCurrentText(self.current_branch)
            self.branch_combo.blockSignals(False)
