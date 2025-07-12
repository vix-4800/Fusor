from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QSizePolicy


class SettingsTab(QWidget):
    """Tab with simple settings form."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QFormLayout(self)

        self.git_url_edit = QLineEdit()
        layout.addRow("Git URL:", self.git_url_edit)

        self.project_path_edit = QLineEdit()
        layout.addRow("Project Path:", self.project_path_edit)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "None"])
        layout.addRow("Framework:", self.framework_combo)

        save_btn = QPushButton("Save")
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.clicked.connect(self.main_window.save_settings)
        layout.addRow(save_btn)

        # expose widgets for use in MainWindow
        self.main_window.git_url_edit = self.git_url_edit
        self.main_window.project_path_edit = self.project_path_edit
        self.main_window.framework_combo = self.framework_combo
