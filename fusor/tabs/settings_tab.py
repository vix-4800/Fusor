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

        self.project_combo = QComboBox()
        self.project_combo.addItems(self.main_window.projects)
        self.project_combo.setCurrentText(self.main_window.project_path)
        self.project_combo.currentTextChanged.connect(self.main_window.set_current_project)

        add_btn = QPushButton("Add")
        add_btn.setFixedHeight(30)
        add_btn.clicked.connect(self.add_project)
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedHeight(30)
        remove_btn.clicked.connect(self.remove_project)
        self.remove_btn = remove_btn
        project_row = QHBoxLayout()
        project_row.addWidget(self.project_combo)
        project_row.addWidget(add_btn)
        project_row.addWidget(remove_btn)
        form.addRow("Project:", self._wrap(project_row))

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

        self.compose_files_edit = QLineEdit(";".join(self.main_window.compose_files))
        self.compose_browse_btn = QPushButton("Browse")
        self.compose_browse_btn.setFixedHeight(30)
        self.compose_browse_btn.clicked.connect(self.browse_compose_files)
        compose_row = QHBoxLayout()
        compose_row.addWidget(self.compose_files_edit)
        compose_row.addWidget(self.compose_browse_btn)
        self.compose_row = self._wrap(compose_row)
        self.compose_label = QLabel("Compose Files:")
        form.addRow(self.compose_label, self.compose_row)
        
        self.remote_combo = QComboBox()
        remotes = self.main_window.git_tab.get_remotes()
        if remotes:
            self.remote_combo.addItems(remotes)
        if self.main_window.git_remote in remotes:
            self.remote_combo.setCurrentText(self.main_window.git_remote)
        form.addRow("Git Remote:", self.remote_combo)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "None"])
        if self.main_window.framework_choice in ["Laravel", "Yii", "None"]:
            self.framework_combo.setCurrentText(self.main_window.framework_choice)
        self.framework_combo.currentTextChanged.connect(self.on_framework_changed)
        self.framework_combo.currentTextChanged.connect(
            self.main_window.database_tab.on_framework_changed
        )
        form.addRow("Framework:", self.framework_combo)

        self.log_path_edit = QLineEdit(self.main_window.log_path)
        log_browse_btn = QPushButton("Browse")
        log_browse_btn.setFixedHeight(30)
        log_browse_btn.clicked.connect(self.browse_log_path)
        log_path_row = QHBoxLayout()
        log_path_row.addWidget(self.log_path_edit)
        log_path_row.addWidget(log_browse_btn)
        self.log_path_row = self._wrap(log_path_row)
        self.log_path_label = QLabel("Log Path:")
        form.addRow(self.log_path_label, self.log_path_row)

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

        self.main_window.project_combo = self.project_combo
        self.main_window.framework_combo = self.framework_combo
        self.main_window.php_path_edit = self.php_path_edit
        self.main_window.php_service_edit = self.php_service_edit
        self.main_window.server_port_edit = self.server_port_edit
        self.main_window.docker_checkbox = self.docker_checkbox
        self.main_window.yii_template_combo = self.yii_template_combo
        self.main_window.log_path_edit = self.log_path_edit
        self.main_window.remote_combo = self.remote_combo
        self.main_window.compose_files_edit = self.compose_files_edit

        self.on_docker_toggled(self.docker_checkbox.isChecked())
        current_fw = self.framework_combo.currentText()
        self.on_framework_changed(current_fw)
        self.main_window.database_tab.on_framework_changed(current_fw)

        # track unsaved changes
        self.project_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.php_path_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.php_service_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.server_port_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.framework_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.log_path_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.yii_template_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.docker_checkbox.toggled.connect(self.main_window.mark_settings_dirty)

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
        self.compose_files_edit.setEnabled(checked)
        self.compose_browse_btn.setEnabled(checked)
        self.compose_row.setVisible(checked)
        self.compose_label.setVisible(checked)
        if hasattr(self.main_window, "docker_index"):
            self.main_window.tabs.setTabVisible(self.main_window.docker_index, checked)
            self.main_window.tabs.setTabEnabled(self.main_window.docker_index, checked)

    def add_project(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            self.main_window.project_path,
        )
        if directory:
            if directory not in self.main_window.projects:
                self.main_window.projects.append(directory)
                self.project_combo.addItem(directory)
            self.project_combo.setCurrentText(directory)
            self.main_window.set_current_project(directory)
            self.main_window.save_settings()

    def remove_project(self):
        index = self.project_combo.currentIndex()
        if index < 0:
            return
        project = self.project_combo.currentText()
        self.project_combo.removeItem(index)
        if project in self.main_window.projects:
            self.main_window.projects.remove(project)

        if self.main_window.project_path == project:
            new_project = self.project_combo.currentText()
            if new_project:
                self.main_window.set_current_project(new_project)
            else:
                self.main_window.project_path = ""

        self.main_window.save_settings()

    def browse_php_path(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PHP Executable",
            self.php_path_edit.text() or self.main_window.php_path,
        )
        if file:
            self.php_path_edit.setText(file)

    def browse_compose_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Compose Files",
            self.compose_files_edit.text() or self.main_window.project_path,
        )
        if files:
            self.compose_files_edit.setText(";".join(files))

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
        log_visible = text == "Laravel"
        self.log_path_row.setVisible(log_visible)
        self.log_path_label.setVisible(log_visible)
        if hasattr(self.main_window, "database_tab"):
            self.main_window.database_tab.on_framework_changed(text)

