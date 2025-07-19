from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QSizePolicy,
    QMessageBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QScrollArea,
)

from ..icons import get_icon

import subprocess


class GitTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_branch = ""
        self.remote_branches_loaded = False

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

        # --- Branch section ---
        branch_group = QGroupBox("Active Branch")
        branch_layout = QHBoxLayout()
        self.branch_combo = QComboBox()
        self.branch_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)

        branch_layout.addWidget(QLabel("Branch:"))
        branch_layout.addWidget(self.branch_combo)
        branch_group.setLayout(branch_layout)
        outer_layout.addWidget(branch_group)

        # --- Remote branches ---
        remote_group = QGroupBox("Remote Branch")
        remote_layout = QHBoxLayout()
        self.remote_branch_combo = QComboBox()
        self.remote_branch_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.remote_branch_combo.currentTextChanged.connect(
            self.on_remote_branch_changed
        )
        refresh_btn = self._btn(
            "Refresh",
            self.load_remote_branches,
            icon="view-refresh",
        )
        remote_layout.addWidget(QLabel("Branch:"))
        remote_layout.addWidget(self.remote_branch_combo)
        remote_layout.addWidget(refresh_btn)
        remote_group.setLayout(remote_layout)
        outer_layout.addWidget(remote_group)

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

    def load_branches(self):
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
        self.branch_combo.setCurrentText(branch)

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

    def load_remote_branches(self):
        remote = self.main_window.git_remote
        self.remote_branch_combo.blockSignals(True)
        self.remote_branch_combo.clear()
        if not remote:
            self.remote_branch_combo.blockSignals(False)
            return
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
            self.remote_branch_combo.addItems(branches)
        except FileNotFoundError:
            print("Command not found: git")
        finally:
            self.remote_branch_combo.blockSignals(False)
            self.remote_branches_loaded = True

    def checkout_remote_branch(self, branch: str):
        remote = self.main_window.git_remote
        if not remote:
            return
        self.run_git_command("fetch", remote)
        self.run_git_command("checkout", "-t", f"{remote}/{branch}")
        self.current_branch = branch

    def on_remote_branch_changed(self, branch: str):
        if not branch:
            return
        if branch == self.current_branch:
            return
        reply = QMessageBox.question(
            self,
            "Checkout Remote Branch",
            f"Switch to remote branch '{branch}'?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.checkout_remote_branch(branch)
        else:
            self.remote_branch_combo.blockSignals(True)
            self.remote_branch_combo.setCurrentText(self.current_branch)
            self.remote_branch_combo.blockSignals(False)
