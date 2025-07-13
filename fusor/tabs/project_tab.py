from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy

class ProjectTab(QWidget):
    """Tab with common project actions."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        start_btn = QPushButton("Start")
        start_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        start_btn.clicked.connect(self.main_window.start_project)
        layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        stop_btn.clicked.connect(self.main_window.stop_project)
        layout.addWidget(stop_btn)

        phpunit_btn = QPushButton("PHPUnit")
        phpunit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        phpunit_btn.clicked.connect(self.main_window.phpunit)
        layout.addWidget(phpunit_btn)

        self.composer_install_btn = QPushButton("Composer install")
        self.composer_install_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.composer_install_btn.clicked.connect(
            lambda: self.main_window.run_command(["composer", "install"])
        )
        layout.addWidget(self.composer_install_btn)

        self.composer_update_btn = QPushButton("Composer update")
        self.composer_update_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.composer_update_btn.clicked.connect(
            lambda: self.main_window.run_command(["composer", "update"])
        )
        layout.addWidget(self.composer_update_btn)
