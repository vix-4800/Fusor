from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QSizePolicy,
    QHBoxLayout,
    QFileDialog,
    QCheckBox,
    QVBoxLayout,
    QGroupBox,
    QLayout,
    QLabel,
)

from PyQt6.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(20)

        project_group = QGroupBox("Project Settings")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.project_path_edit = QLineEdit(self.main_window.project_path)
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedHeight(30)
        browse_btn.clicked.connect(self.browse_project_path)
        project_path_row = QHBoxLayout()
        project_path_row.addWidget(self.project_path_edit)
        project_path_row.addWidget(browse_btn)
        form.addRow("Project Path:", self._wrap(project_path_row))

        self.php_path_edit = QLineEdit(self.main_window.php_path)
        self.php_browse_btn = QPushButton("Browse")
        self.php_browse_btn.setFixedHeight(30)
        self.php_browse_btn.clicked.connect(self.browse_php_path)
        php_path_row = QHBoxLayout()
        php_path_row.addWidget(self.php_path_edit)
        php_path_row.addWidget(self.php_browse_btn)
        form.addRow("PHP Executable:", self._wrap(php_path_row))

        self.php_service_edit = QLineEdit(self.main_window.php_service)
        form.addRow("PHP Service:", self.php_service_edit)

        self.server_port_edit = QLineEdit(str(self.main_window.server_port))
        form.addRow("Server Port:", self.server_port_edit)

        self.log_path_edit = QLineEdit(self.main_window.log_path)
        log_browse_btn = QPushButton("Browse")
        log_browse_btn.setFixedHeight(30)
        log_browse_btn.clicked.connect(self.browse_log_path)
        log_path_row = QHBoxLayout()
        log_path_row.addWidget(self.log_path_edit)
        log_path_row.addWidget(log_browse_btn)
        self.log_path_row = self._wrap(log_path_row)
        form.addRow("Log Path:", self.log_path_row)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "None"])
        if self.main_window.framework_choice in ["Laravel", "Yii", "None"]:
            self.framework_combo.setCurrentText(self.main_window.framework_choice)
        self.framework_combo.currentTextChanged.connect(self.on_framework_changed)
        form.addRow("Framework:", self.framework_combo)

        self.yii_template_combo = QComboBox()
        self.yii_template_combo.addItems(["basic", "advanced"])
        if hasattr(self.main_window, "yii_template"):
            self.yii_template_combo.setCurrentText(self.main_window.yii_template)
        self.yii_template_row = self._wrap(self.yii_template_combo)
        self.yii_template_label = QLabel("Yii Template:")
        form.addRow(self.yii_template_label, self.yii_template_row)

        self.docker_checkbox = QCheckBox("Use Docker")
        self.docker_checkbox.setChecked(self.main_window.use_docker)
        self.docker_checkbox.setMinimumHeight(30)
        self.docker_checkbox.toggled.connect(self.on_docker_toggled)
        form.addRow("", self.docker_checkbox)

        project_group.setLayout(form)
        outer_layout.addWidget(project_group)

        save_btn = QPushButton("💾 Save Settings")
        save_btn.setMinimumHeight(36)
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.clicked.connect(self.main_window.save_settings)
        outer_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_window.project_path_edit = self.project_path_edit
        self.main_window.framework_combo = self.framework_combo
        self.main_window.php_path_edit = self.php_path_edit
        self.main_window.php_service_edit = self.php_service_edit
        self.main_window.server_port_edit = self.server_port_edit
        self.main_window.docker_checkbox = self.docker_checkbox
        self.main_window.yii_template_combo = self.yii_template_combo
        self.main_window.log_path_edit = self.log_path_edit

        self.on_docker_toggled(self.docker_checkbox.isChecked())
        self.on_framework_changed(self.framework_combo.currentText())

    def _wrap(self, child):
        """Return a QWidget containing the given layout or widget."""
        container = QWidget()
        if isinstance(child, QLayout):
            container.setLayout(child)
        else:
            layout = QHBoxLayout()
            layout.addWidget(child)
            container.setLayout(layout)
        return container

    def on_docker_toggled(self, checked: bool):
        self.php_path_edit.setEnabled(not checked)
        self.php_browse_btn.setEnabled(not checked)
        self.php_service_edit.setEnabled(checked)

    def browse_project_path(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            self.project_path_edit.text() or self.main_window.project_path,
        )
        if directory:
            self.project_path_edit.setText(directory)

    def browse_php_path(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PHP Executable",
            self.php_path_edit.text() or self.main_window.php_path,
        )
        if file:
            self.php_path_edit.setText(file)

    def browse_log_path(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            self.log_path_edit.text() or self.main_window.log_path,
        )
        if file:
            self.log_path_edit.setText(file)

    def on_framework_changed(self, text: str):
        visible = text == "Yii"
        self.yii_template_row.setVisible(visible)
        self.yii_template_label.setVisible(visible)
        self.log_path_row.setVisible(text == "Laravel")

