from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QMessageBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QDialog,
)

from ..icons import get_icon
from ..branch_dialog import BranchDialog

import subprocess


class GitTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_branch = ""

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(16)

        # --- Branch section ---
        branch_group = QGroupBox("Active Branch")
        branch_layout = QHBoxLayout()
        self.current_branch_label = QLabel("")
        checkout_btn = self._btn(
            "Checkout...",
            self.show_branch_dialog,
            icon="document-open",
        )

        branch_layout.addWidget(QLabel("Current:"))
        branch_layout.addWidget(self.current_branch_label)
        branch_layout.addStretch(1)
        branch_layout.addWidget(checkout_btn)
        branch_group.setLayout(branch_layout)
        outer_layout.addWidget(branch_group)

        # --- Create branch ---
        create_group = QGroupBox("Create Branch")
        create_layout = QHBoxLayout()
        self.branch_name_edit = QLineEdit()
        create_btn = self._btn(
            "Create Branch",
            self.create_branch,
            icon="list-add",
        )
        create_layout.addWidget(self.branch_name_edit)
        create_layout.addWidget(create_btn)
        create_group.setLayout(create_layout)
        outer_layout.addWidget(create_group)

        # --- Git actions ---
        actions_group = QGroupBox("Git Commands")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)

        pull_btn = self._btn(
            "Pull",
            lambda: self.run_git_command("pull"),
            icon="go-down",
        )
        push_btn = self._btn(
            "Push",
            lambda: self.run_git_command("push"),
            icon="go-up",
        )
        reset_btn = self._btn(
            "Hard Reset",
            self.hard_reset,
            icon="edit-undo",
        )
        stash_btn = self._btn(
            "Stash",
            self.stash,
            icon="document-save",
        )
        status_btn = self._btn(
            "Status",
            self.show_status,
            icon="dialog-information",
        )
        diff_btn = self._btn(
            "Diff",
            self.show_diff,
            icon="document-diff",
        )
        view_log_btn = self._btn(
            "View Log",
            self.view_log,
            icon="text-x-generic",
        )

        actions_layout.addWidget(pull_btn)
        actions_layout.addWidget(push_btn)
        actions_layout.addWidget(reset_btn)
        actions_layout.addWidget(stash_btn)
        actions_layout.addWidget(status_btn)
        actions_layout.addWidget(diff_btn)
        actions_layout.addWidget(view_log_btn)

        actions_group.setLayout(actions_layout)
        outer_layout.addWidget(actions_group)

        outer_layout.addStretch(1)

    def _btn(self, label, slot, icon: str | None = None):
        btn = QPushButton(label)
        if icon:
            btn.setIcon(get_icon(icon))
        btn.setMinimumHeight(36)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot)
        return btn

    def run_git_command(self, *args):
        if not self.main_window.ensure_project_path():
            return
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

    def fetch_local_branches(self) -> list[str]:
        if not self.main_window.project_path:
            return []
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            return [b.strip() for b in result.stdout.splitlines() if b.strip()]
        except FileNotFoundError:
            print("Command not found: git")
            return []

    def fetch_remote_branches(self) -> list[str]:
        remote = self.main_window.git_remote
        if not remote or not self.main_window.project_path:
            return []
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", remote],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            branches = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1].startswith("refs/heads/"):
                    branches.append(parts[1].split("/", 2)[2])
            return branches
        except FileNotFoundError:
            print("Command not found: git")
            return []

    def show_branch_dialog(self):
        local = self.fetch_local_branches()
        remote = [f"{self.main_window.git_remote}/{b}" for b in self.fetch_remote_branches()]
        dialog = BranchDialog(local + remote, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            branch = dialog.get_branch()
            if not branch:
                return
            if "/" in branch:
                _remote, b = branch.split("/", 1)
                self.checkout_remote_branch(b)
            else:
                self.checkout(branch)
            self.load_branches()

    def load_branches(self):
        if not self.main_window.project_path:
            return
        _ = self.fetch_local_branches()

        try:
            head = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            current = head.stdout.strip()
        except FileNotFoundError:
            print("Command not found: git")
            current = ""
        self.current_branch = current
        self.current_branch_label.setText(current)

    def checkout(self, branch):
        self.main_window.ensure_project_path()
        self.run_git_command("checkout", branch)
        self.current_branch = branch
        self.current_branch_label.setText(branch)

    def hard_reset(self):
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
        if not self.main_window.ensure_project_path():
            return
        result = self.run_git_command("stash")
        if result and result.returncode == 0:
            print("Changes stashed successfully")
        else:
            print("Stash failed")

    def view_log(self):
        """Show recent git log entries."""
        self.run_git_command("log", "-n", "20", "--oneline")

    def show_status(self):
        """Display git status."""
        self.run_git_command("status")

    def show_diff(self):
        """Display git diff."""
        self.run_git_command("diff")

    def create_branch(self):
        branch = self.branch_name_edit.text().strip()
        if not branch:
            return
        self.run_git_command("checkout", "-b", branch)
        self.load_branches()
        self.current_branch_label.setText(branch)

    def get_remotes(self) -> list[str]:
        if not self.main_window.project_path:
            return []
        try:
            res = subprocess.run(
                ["git", "remote"],
                capture_output=True,
                text=True,
                cwd=self.main_window.project_path,
            )
            return [r.strip() for r in res.stdout.splitlines() if r.strip()]
        except FileNotFoundError:
            return []

    def checkout_remote_branch(self, branch: str):
        remote = self.main_window.git_remote
        if not remote:
            return
        self.run_git_command("fetch", remote)
        self.run_git_command("checkout", "-t", f"{remote}/{branch}")
        self.current_branch = branch
        self.current_branch_label.setText(branch)
