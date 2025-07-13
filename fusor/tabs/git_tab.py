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
        """Initialize the Git tab UI.

        Parameters
        ----------
        main_window : MainWindow
            Parent window used to run commands.
        """
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        self.branch_combo = QComboBox()
        self.branch_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.branch_combo)

        self.current_branch = ""
        # branches are loaded once the project path is available
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)

        pull_btn = QPushButton("Pull")
        pull_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pull_btn.clicked.connect(lambda: self.run_git_command("pull"))
        layout.addWidget(pull_btn)

        hard_reset_btn = QPushButton("Hard reset")
        hard_reset_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        hard_reset_btn.clicked.connect(self.hard_reset)
        layout.addWidget(hard_reset_btn)

        stash_btn = QPushButton("Stash")
        stash_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        stash_btn.clicked.connect(self.stash)
        layout.addWidget(stash_btn)

    def run_git_command(self, *args):
        """Run a Git command inside the project directory."""

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
            return result
        except FileNotFoundError:
            print("Command not found: git")
            return None

    def load_branches(self):
        """Populate the branch combo if a project path is available."""
        if not self.main_window.project_path:
            return
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
        """Switch to ``branch`` if possible."""

        self.main_window.ensure_project_path()
        self.run_git_command("checkout", branch)
        self.current_branch = branch

    def on_branch_changed(self, branch):
        """Handle branch selection changes."""

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

    def hard_reset(self):
        """Perform a hard reset with confirmation."""
        if not self.main_window.ensure_project_path():
            return

        reply = QMessageBox.question(
            self,
            "Hard Reset",
            "Discard all local changes and reset to HEAD?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.run_git_command("reset", "--hard")
            if result and result.returncode == 0:
                print("Hard reset successful")
            else:
                print("Hard reset failed")

    def stash(self):
        """Stash current changes."""
        if not self.main_window.ensure_project_path():
            return
        result = self.run_git_command("stash")
        if result and result.returncode == 0:
            print("Changes stashed successfully")
        else:
            print("Stash failed")
