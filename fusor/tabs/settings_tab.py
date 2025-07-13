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

        self.git_url_edit = QLineEdit()
        self.git_url_edit.setText(self.main_window.git_url)
        layout.addRow("Git URL:", self.git_url_edit)

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
        self.main_window.git_url_edit = self.git_url_edit
        self.main_window.project_path_edit = self.project_path_edit
        self.main_window.framework_combo = self.framework_combo

    def browse_project_path(self):
        """Open a folder selection dialog and update the path field."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            self.project_path_edit.text() or self.main_window.project_path,
        )
        if directory:
            self.project_path_edit.setText(directory)

