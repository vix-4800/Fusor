from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QSizePolicy,
    QHBoxLayout,
    QFileDialog,
)

class SettingsTab(QWidget):
    """Tab with simple settings form."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QFormLayout(self)


        self.project_path_edit = QLineEdit()
        self.project_path_edit.setText(self.main_window.project_path)
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.project_path_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_project_path)
        path_layout.addWidget(browse_btn)
        layout.addRow("Project Path:", path_container)

        self.php_path_edit = QLineEdit()
        self.php_path_edit.setText(self.main_window.php_path)
        php_container = QWidget()
        php_layout = QHBoxLayout(php_container)
        php_layout.setContentsMargins(0, 0, 0, 0)
        php_layout.addWidget(self.php_path_edit)
        php_browse_btn = QPushButton("Browse")
        php_browse_btn.clicked.connect(self.browse_php_path)
        php_layout.addWidget(php_browse_btn)
        layout.addRow("PHP Executable:", php_container)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "None"])
        if self.main_window.framework_choice in ["Laravel", "Yii", "None"]:
            self.framework_combo.setCurrentText(self.main_window.framework_choice)
        layout.addRow("Framework:", self.framework_combo)

        save_btn = QPushButton("Save")
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.clicked.connect(self.main_window.save_settings)
        layout.addRow(save_btn)

        # expose widgets for use in MainWindow
        self.main_window.project_path_edit = self.project_path_edit
        self.main_window.framework_combo = self.framework_combo
        self.main_window.php_path_edit = self.php_path_edit

    def browse_project_path(self):
        """Open a folder selection dialog and update the path field."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            self.project_path_edit.text() or self.main_window.project_path,
        )
        if directory:
            self.project_path_edit.setText(directory)

    def browse_php_path(self):
        """Open a file selection dialog for the PHP executable."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PHP Executable",
            self.php_path_edit.text() or self.main_window.php_path,
        )
        if file:
            self.php_path_edit.setText(file)

