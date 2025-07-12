import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QTextEdit,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusor – Laravel/PHP QA Toolbox")
        # open the window at a convenient default size
        self.resize(1024, 768)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_project_tab()
        self.init_git_tab()
        self.init_database_tab()
        self.init_logs_tab()

    def init_project_tab(self):
        project_tab = QWidget()
        layout = QVBoxLayout(project_tab)

        migrate_btn = QPushButton("Migrate")
        migrate_btn.clicked.connect(lambda: print("Migrate clicked"))
        layout.addWidget(migrate_btn)

        rollback_btn = QPushButton("Rollback")
        rollback_btn.clicked.connect(lambda: print("Rollback clicked"))
        layout.addWidget(rollback_btn)

        fresh_btn = QPushButton("Fresh")
        fresh_btn.clicked.connect(lambda: print("Fresh clicked"))
        layout.addWidget(fresh_btn)

        seed_btn = QPushButton("Seed")
        seed_btn.clicked.connect(lambda: print("Seed clicked"))
        layout.addWidget(seed_btn)

        self.tabs.addTab(project_tab, "Project")

    def init_git_tab(self):
        git_tab = QWidget()
        layout = QVBoxLayout(git_tab)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems(["main", "dev", "feature/example"])
        layout.addWidget(self.branch_combo)

        checkout_btn = QPushButton("Checkout")
        checkout_btn.clicked.connect(lambda: print(f"Checkout {self.branch_combo.currentText()}"))
        layout.addWidget(checkout_btn)

        pull_btn = QPushButton("Pull")
        pull_btn.clicked.connect(lambda: print("Pull clicked"))
        layout.addWidget(pull_btn)

        hard_reset_btn = QPushButton("Hard reset")
        hard_reset_btn.clicked.connect(lambda: print("Hard reset clicked"))
        layout.addWidget(hard_reset_btn)

        stash_btn = QPushButton("Stash")
        stash_btn.clicked.connect(lambda: print("Stash clicked"))
        layout.addWidget(stash_btn)

        self.tabs.addTab(git_tab, "Git")

    def init_database_tab(self):
        db_tab = QWidget()
        layout = QVBoxLayout(db_tab)

        dbeaver_btn = QPushButton("Open in DBeaver")
        dbeaver_btn.clicked.connect(lambda: print("Open in DBeaver clicked"))
        layout.addWidget(dbeaver_btn)

        dump_btn = QPushButton("Dump to SQL")
        dump_btn.clicked.connect(lambda: print("Dump to SQL clicked"))
        layout.addWidget(dump_btn)

        restore_btn = QPushButton("Restore dump")
        restore_btn.clicked.connect(lambda: print("Restore dump clicked"))
        layout.addWidget(restore_btn)

        self.tabs.addTab(db_tab, "Database")

    def init_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlainText("Example log line 1\nExample log line 2")
        layout.addWidget(self.log_view)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_logs)
        layout.addWidget(refresh_btn)

        self.tabs.addTab(logs_tab, "Logs")

    def refresh_logs(self):
        print("Refresh logs clicked")
        self.log_view.setPlainText("Example log line 1\nExample log line 2\nExample log line 3")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
