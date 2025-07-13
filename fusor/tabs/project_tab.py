from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)

class ProjectTab(QWidget):
    """Tab with common project actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        start_btn = QPushButton("Start")
        start_btn.setMinimumHeight(40)
        start_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        start_btn.clicked.connect(self.main_window.start_project)

        stop_btn = QPushButton("Stop")
        stop_btn.setMinimumHeight(40)
        stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stop_btn.clicked.connect(self.main_window.stop_project)

        top_row = QHBoxLayout()
        top_row.addWidget(start_btn)
        top_row.addWidget(stop_btn)
        layout.addLayout(top_row)

        phpunit_btn = QPushButton("PHPUnit")
        phpunit_btn.setMinimumHeight(30)
        phpunit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        phpunit_btn.clicked.connect(self.main_window.phpunit)
        layout.addWidget(phpunit_btn)

        self.composer_install_btn = QPushButton("Composer install")
        self.composer_install_btn.setMinimumHeight(30)
        self.composer_install_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.composer_install_btn.clicked.connect(
            lambda: self.main_window.run_command(["composer", "install"])
        )
        layout.addWidget(self.composer_install_btn)

        self.composer_update_btn = QPushButton("Composer update")
        self.composer_update_btn.setMinimumHeight(30)
        self.composer_update_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.composer_update_btn.clicked.connect(
            lambda: self.main_window.run_command(["composer", "update"])
        )
        layout.addWidget(self.composer_update_btn)
