import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QTextEdit,
    QSizePolicy,
    QLineEdit,
    QFormLayout,
    QMessageBox,
)


class QTextEditLogger:
    """Redirects writes to both stdout and a QTextEdit widget."""

    def __init__(self, text_edit, original_stdout):
        self.text_edit = text_edit
        self.original_stdout = original_stdout

    def write(self, msg):
        if msg.rstrip():
            # Append text to the widget without extra newlines
            self.text_edit.append(msg.rstrip())
        self.original_stdout.write(msg)

    def flush(self):
        self.original_stdout.flush()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusor – Laravel/PHP QA Toolbox")
        self.resize(1024, 768)

        self.tabs = QTabWidget()
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.output_view)
        self.setCentralWidget(central_widget)

        # Redirect stdout to the output view
        self._stdout_logger = QTextEditLogger(self.output_view, sys.stdout)
        sys.stdout = self._stdout_logger

        self.init_project_tab()
        self.init_git_tab()
        self.init_database_tab()
        self.init_logs_tab()
        self.init_settings_tab()

    def run_command(self, command):
        """Run a shell command and print its output."""
        print(f"$ {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip())
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")

    def current_framework(self):
        return self.framework_combo.currentText() if hasattr(self, 'framework_combo') else "None"

    def init_project_tab(self):
        project_tab = QWidget()
        layout = QVBoxLayout(project_tab)

        migrate_btn = QPushButton("Migrate")
        migrate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        migrate_btn.clicked.connect(self.migrate)
        layout.addWidget(migrate_btn)

        rollback_btn = QPushButton("Rollback")
        rollback_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        rollback_btn.clicked.connect(self.rollback)
        layout.addWidget(rollback_btn)

        fresh_btn = QPushButton("Fresh")
        fresh_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        fresh_btn.clicked.connect(self.fresh)
        layout.addWidget(fresh_btn)

        seed_btn = QPushButton("Seed")
        seed_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        seed_btn.clicked.connect(self.seed)
        layout.addWidget(seed_btn)

        self.tabs.addTab(project_tab, "Project")

    def init_git_tab(self):
        git_tab = QWidget()
        layout = QVBoxLayout(git_tab)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems(["main", "dev", "feature/example"])
        self.branch_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.branch_combo)

        checkout_btn = QPushButton("Checkout")
        checkout_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        checkout_btn.clicked.connect(lambda: print(f"Checkout {self.branch_combo.currentText()}"))
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

        self.tabs.addTab(git_tab, "Git")

    def init_database_tab(self):
        db_tab = QWidget()
        layout = QVBoxLayout(db_tab)

        dbeaver_btn = QPushButton("Open in DBeaver")
        dbeaver_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dbeaver_btn.clicked.connect(lambda: print("Open in DBeaver clicked"))
        layout.addWidget(dbeaver_btn)

        dump_btn = QPushButton("Dump to SQL")
        dump_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dump_btn.clicked.connect(lambda: print("Dump to SQL clicked"))
        layout.addWidget(dump_btn)

        restore_btn = QPushButton("Restore dump")
        restore_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        restore_btn.clicked.connect(lambda: print("Restore dump clicked"))
        layout.addWidget(restore_btn)

        self.tabs.addTab(db_tab, "Database")

    def init_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlainText("Example log line 1\nExample log line 2")
        self.log_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.log_view)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        refresh_btn.clicked.connect(self.refresh_logs)
        layout.addWidget(refresh_btn)

        self.tabs.addTab(logs_tab, "Logs")

    def init_settings_tab(self):
        settings_tab = QWidget()
        layout = QFormLayout(settings_tab)

        self.git_url_edit = QLineEdit()
        layout.addRow("Git URL:", self.git_url_edit)

        self.var1_edit = QLineEdit()
        layout.addRow("Variable 1:", self.var1_edit)

        self.var2_edit = QLineEdit()
        layout.addRow("Variable 2:", self.var2_edit)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "None"])
        layout.addRow("Framework:", self.framework_combo)

        save_btn = QPushButton("Save")
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.clicked.connect(self.save_settings)
        layout.addRow(save_btn)

        self.tabs.addTab(settings_tab, "Settings")

    def refresh_logs(self):
        print("Refresh logs clicked")
        self.log_view.setPlainText("Example log line 1\nExample log line 2\nExample log line 3")

    def save_settings(self):
        git_url = self.git_url_edit.text()
        var1 = self.var1_edit.text()
        var2 = self.var2_edit.text()
        framework = self.framework_combo.currentText()
        
        if not git_url or not var1 or not var2:
            QMessageBox.warning(self, "Invalid settings", "All settings fields must be filled out.")
            print("Failed to save settings: one or more fields were empty")
            return

        print(
            f"Settings saved: Git URL={git_url}, Variable 1={var1}, Variable 2={var2}, Framework={framework}"
        )

    def migrate(self):
        if self.current_framework() == "Laravel":
            self.run_command(["php", "artisan", "migrate"])
        else:
            print(f"Migrate not implemented for {self.current_framework()}")

    def rollback(self):
        if self.current_framework() == "Laravel":
            self.run_command(["php", "artisan", "migrate:rollback"])
        else:
            print(f"Rollback not implemented for {self.current_framework()}")

    def fresh(self):
        if self.current_framework() == "Laravel":
            self.run_command(["php", "artisan", "migrate:fresh"])
        else:
            print(f"Fresh not implemented for {self.current_framework()}")

    def seed(self):
        if self.current_framework() == "Laravel":
            self.run_command(["php", "artisan", "db:seed"])
        else:
            print(f"Seed not implemented for {self.current_framework()}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
