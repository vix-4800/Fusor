import os
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
    QSpinBox,
)

from PyQt6.QtCore import Qt
from ..icons import get_icon

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
        for proj in self.main_window.projects:
            self.project_combo.addItem(proj["name"], proj["path"])
        idx = self.project_combo.findData(self.main_window.project_path)
        if idx >= 0:
            self.project_combo.setCurrentIndex(idx)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)

        add_btn = QPushButton("Add")
        add_btn.setIcon(get_icon("list-add"))
        add_btn.setFixedHeight(30)
        add_btn.clicked.connect(self.add_project)
        remove_btn = QPushButton("Remove")
        remove_btn.setIcon(get_icon("list-remove"))
        remove_btn.setFixedHeight(30)
        remove_btn.clicked.connect(self.remove_project)
        self.remove_btn = remove_btn
        project_row = QHBoxLayout()
        project_row.addWidget(self.project_combo)
        project_row.addWidget(add_btn)
        project_row.addWidget(remove_btn)
        form.addRow("Project:", self._wrap(project_row))

        self.project_name_edit = QLineEdit()
        name = ""
        for p in self.main_window.projects:
            if p.get("path") == self.main_window.project_path:
                name = p.get("name", "")
                break
        self.project_name_edit.setText(name)
        form.addRow("Project Name:", self.project_name_edit)

        self.php_path_edit = QLineEdit(self.main_window.php_path)
        self.php_browse_btn = QPushButton("Browse")
        self.php_browse_btn.setIcon(get_icon("document-open"))
        self.php_browse_btn.setFixedHeight(30)
        self.php_browse_btn.clicked.connect(self.browse_php_path)
        php_path_row = QHBoxLayout()
        php_path_row.addWidget(self.php_path_edit)
        php_path_row.addWidget(self.php_browse_btn)
        form.addRow("PHP Executable:", self._wrap(php_path_row))

        self.php_service_edit = QLineEdit(self.main_window.php_service)
        form.addRow("PHP Service:", self.php_service_edit)

        self.server_port_edit = QSpinBox()
        self.server_port_edit.setRange(1, 65535)
        self.server_port_edit.setValue(self.main_window.server_port)
        form.addRow("Server Port:", self.server_port_edit)

        self.compose_files_edit = QLineEdit(";".join(self.main_window.compose_files))
        self.compose_browse_btn = QPushButton("Browse")
        self.compose_browse_btn.setIcon(get_icon("document-open"))
        self.compose_browse_btn.setFixedHeight(30)
        self.compose_browse_btn.clicked.connect(self.browse_compose_files)
        compose_row = QHBoxLayout()
        compose_row.addWidget(self.compose_files_edit)
        compose_row.addWidget(self.compose_browse_btn)
        self.compose_row = self._wrap(compose_row)
        self.compose_label = QLabel("Compose Files:")
        form.addRow(self.compose_label, self.compose_row)

        self.compose_profile_edit = QLineEdit(self.main_window.compose_profile)
        form.addRow("Compose Profile:", self.compose_profile_edit)

        self.remote_combo = QComboBox()
        remotes = self.main_window.git_tab.get_remotes()
        if remotes:
            self.remote_combo.addItems(remotes)
        if self.main_window.git_remote in remotes:
            self.remote_combo.setCurrentText(self.main_window.git_remote)
        form.addRow("Git Remote:", self.remote_combo)

        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Laravel", "Yii", "Symfony", "None"])
        if self.main_window.framework_choice in ["Laravel", "Yii", "Symfony", "None"]:
            self.framework_combo.setCurrentText(self.main_window.framework_choice)
        self.framework_combo.currentTextChanged.connect(self.on_framework_changed)
        self.framework_combo.currentTextChanged.connect(
            self.main_window.database_tab.on_framework_changed
        )
        if hasattr(self.main_window, "laravel_tab"):
            self.framework_combo.currentTextChanged.connect(
                self.main_window.laravel_tab.on_framework_changed
            )
        if hasattr(self.main_window, "symfony_tab"):
            self.framework_combo.currentTextChanged.connect(
                self.main_window.symfony_tab.on_framework_changed
            )
        form.addRow("Framework:", self.framework_combo)

        self.log_path_edits: list[QLineEdit] = []
        self.log_paths_layout = QVBoxLayout()

        for path in getattr(self.main_window, "log_paths", [self.main_window.log_path]):
            self._add_log_path_field(path)

        self.log_paths_container = self._wrap(self.log_paths_layout)
        self.log_path_label = QLabel("Log Paths:")
        form.addRow(self.log_path_label, self.log_paths_container)

        add_log_btn = QPushButton("Add Log Path")
        add_log_btn.setIcon(get_icon("list-add"))
        add_log_btn.setFixedHeight(30)
        add_log_btn.clicked.connect(lambda: self._add_log_path_field(""))
        self.add_log_btn = add_log_btn
        form.addRow("", self._wrap(add_log_btn))

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 3600)
        self.refresh_spin.setValue(self.main_window.auto_refresh_secs)
        form.addRow("Auto refresh (seconds):", self.refresh_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        if getattr(self.main_window, "theme", "dark") == "light":
            self.theme_combo.setCurrentText("Light")
        form.addRow("Theme:", self.theme_combo)

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

        save_btn = QPushButton("Save Settings")
        save_btn.setIcon(get_icon("document-save"))
        save_btn.setMinimumHeight(36)
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        save_btn.clicked.connect(self.main_window.save_settings)
        outer_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_window.project_combo = self.project_combo
        self.main_window.project_name_edit = self.project_name_edit
        self.main_window.framework_combo = self.framework_combo
        self.main_window.php_path_edit = self.php_path_edit
        self.main_window.php_service_edit = self.php_service_edit
        self.main_window.server_port_edit = self.server_port_edit
        self.main_window.docker_checkbox = self.docker_checkbox
        self.main_window.yii_template_combo = self.yii_template_combo
        self.main_window.log_path_edit = self.log_path_edit
        self.main_window.remote_combo = self.remote_combo
        self.main_window.compose_files_edit = self.compose_files_edit
        self.main_window.compose_profile_edit = self.compose_profile_edit
        self.main_window.refresh_spin = self.refresh_spin
        self.main_window.theme_combo = self.theme_combo

        self.on_docker_toggled(self.docker_checkbox.isChecked())
        current_fw = self.framework_combo.currentText()
        self.on_framework_changed(current_fw)
        self.main_window.database_tab.on_framework_changed(current_fw)
        if hasattr(self.main_window, "laravel_tab"):
            self.main_window.laravel_tab.on_framework_changed(current_fw)
        if hasattr(self.main_window, "symfony_tab"):
            self.main_window.symfony_tab.on_framework_changed(current_fw)

        # track unsaved changes
        self.project_combo.currentIndexChanged.connect(lambda _: self.main_window.mark_settings_dirty())
        self.php_path_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.php_service_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.server_port_edit.valueChanged.connect(self.main_window.mark_settings_dirty)
        self.framework_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.yii_template_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.docker_checkbox.toggled.connect(self.main_window.mark_settings_dirty)
        self.refresh_spin.valueChanged.connect(self.main_window.mark_settings_dirty)
        self.theme_combo.currentTextChanged.connect(self.main_window.mark_settings_dirty)
        self.project_name_edit.textChanged.connect(self.main_window.mark_settings_dirty)
        self.compose_profile_edit.textChanged.connect(self.main_window.mark_settings_dirty)

    def _on_project_changed(self, _index: int) -> None:
        path = self.project_combo.currentData()
        self.main_window.set_current_project(path)
        name = ""
        for p in self.main_window.projects:
            if p.get("path") == path:
                name = p.get("name", os.path.basename(path))
                break
        self.project_name_edit.blockSignals(True)
        self.project_name_edit.setText(name)
        self.project_name_edit.blockSignals(False)

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

    def _add_log_path_field(self, value: str) -> None:
        edit = QLineEdit(value)
        browse = QPushButton("Browse")
        browse.setIcon(get_icon("document-open"))
        browse.setFixedHeight(30)
        browse.clicked.connect(lambda: self.browse_log_path(edit))
        remove = QPushButton("Remove")
        remove.setIcon(get_icon("list-remove"))
        remove.setFixedHeight(30)

        row = QHBoxLayout()
        row.addWidget(edit)
        row.addWidget(browse)
        row.addWidget(remove)
        container = QWidget()
        container.setLayout(row)
        self.log_paths_layout.addWidget(container)
        self.log_path_edits.append(edit)
        self._log_path_rows = getattr(self, "_log_path_rows", [])
        self._log_path_rows.append(container)
        remove.clicked.connect(lambda: self._remove_log_path_field(container, edit))
        edit.textChanged.connect(self.main_window.mark_settings_dirty)
        if len(self.log_path_edits) == 1:
            self.log_path_edit = edit
            self.main_window.log_path_edit = edit

    def _remove_log_path_field(self, widget: QWidget, edit: QLineEdit) -> None:
        self.log_paths_layout.removeWidget(widget)
        widget.deleteLater()
        if edit in self.log_path_edits:
            self.log_path_edits.remove(edit)
        if hasattr(self, "_log_path_rows") and widget in self._log_path_rows:
            self._log_path_rows.remove(widget)
        if not self.log_path_edits:
            self._add_log_path_field("")
        self.log_path_edit = self.log_path_edits[0]
        self.main_window.log_path_edit = self.log_path_edit
        self.main_window.mark_settings_dirty()

    def set_log_paths(self, paths: list[str]) -> None:
        for widget in list(getattr(self, "_log_path_rows", [])):
            self.log_paths_layout.removeWidget(widget)
            widget.deleteLater()
        self.log_path_edits.clear()
        self._log_path_rows = []
        for p in paths:
            self._add_log_path_field(p)
        if self.log_path_edits:
            self.log_path_edit = self.log_path_edits[0]
            self.main_window.log_path_edit = self.log_path_edit

    def on_docker_toggled(self, checked: bool):
        self.php_path_edit.setEnabled(not checked)
        self.php_browse_btn.setEnabled(not checked)
        self.php_service_edit.setEnabled(checked)
        self.server_port_edit.setEnabled(not checked)
        self.compose_files_edit.setEnabled(checked)
        self.compose_browse_btn.setEnabled(checked)
        self.compose_row.setEnabled(checked)
        self.compose_label.setEnabled(checked)
        self.compose_profile_edit.setEnabled(checked)
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
            if not any(p.get("path") == directory for p in self.main_window.projects):
                name = os.path.basename(directory)
                self.main_window.projects.append({"path": directory, "name": name})
                self.project_combo.addItem(name, directory)
            idx = self.project_combo.findData(directory)
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
            self.main_window.set_current_project(directory)
            framework = self.framework_combo.currentText()
            if os.path.isfile(os.path.join(directory, "artisan")):
                framework = "Laravel"
            elif any(
                os.path.isfile(os.path.join(directory, name))
                for name in ["yii", "yii.bat"]
            ):
                framework = "Yii"
            elif os.path.isfile(os.path.join(directory, "bin", "console")):
                framework = "Symfony"
            self.framework_combo.setCurrentText(framework)
            if hasattr(self.main_window, "framework_combo"):
                self.main_window.framework_combo.setCurrentText(framework)
            self.main_window.save_settings()

    def remove_project(self):
        index = self.project_combo.currentIndex()
        if index < 0:
            return
        path = self.project_combo.itemData(index)
        self.project_combo.removeItem(index)
        self.main_window.projects = [p for p in self.main_window.projects if p.get("path") != path]

        if self.main_window.project_path == path:
            new_path = self.project_combo.currentData()
            if new_path:
                self.main_window.set_current_project(new_path)
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

    def browse_log_path(self, edit: QLineEdit):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            edit.text() or self.main_window.log_path,
        )
        if file:
            edit.setText(file)

    def on_framework_changed(self, text: str):
        visible = text == "Yii"
        self.yii_template_row.setVisible(visible)
        self.yii_template_label.setVisible(visible)

        log_visible = text == "Laravel"
        self.log_paths_container.setVisible(log_visible)
        self.log_path_label.setVisible(log_visible)
        self.add_log_btn.setVisible(log_visible)

        for attr in ["database_tab", "laravel_tab", "symfony_tab"]:
            tab = getattr(self.main_window, attr, None)
            if tab is not None:
                tab.on_framework_changed(text)

        tab_map = {
            "laravel_index": "Laravel",
            "symfony_index": "Symfony",
        }
        for index_attr, fw in tab_map.items():
            if hasattr(self.main_window, index_attr):
                idx = getattr(self.main_window, index_attr)
                show = text == fw
                self.main_window.tabs.setTabVisible(idx, show)
                self.main_window.tabs.setTabEnabled(idx, show)

