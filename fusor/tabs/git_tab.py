from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QSizePolicy, QMessageBox, QGroupBox, QLabel
)

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
        self.branch_combo = QComboBox()
        self.branch_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)

        branch_layout.addWidget(QLabel("Branch:"))
        branch_layout.addWidget(self.branch_combo)
        branch_group.setLayout(branch_layout)
        outer_layout.addWidget(branch_group)

        # --- Git actions ---
        actions_group = QGroupBox("Git Commands")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)

        pull_btn = self._btn("⬇ Pull", lambda: self.run_git_command("pull"))
        reset_btn = self._btn("↩ Hard Reset", self.hard_reset)
        stash_btn = self._btn("💾 Stash", self.stash)

        actions_layout.addWidget(pull_btn)
        actions_layout.addWidget(reset_btn)
        actions_layout.addWidget(stash_btn)

        actions_group.setLayout(actions_layout)
        outer_layout.addWidget(actions_group)

        outer_layout.addStretch(1)

    def _btn(self, label, slot):
        btn = QPushButton(label)
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
