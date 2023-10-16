from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout


class AppEditDialog(QDialog):
    def __init__(self, app_data=None):
        super().__init__()

        self.app_data = app_data if app_data else {}
        self.form_layout = QFormLayout()
        self.name_edit = QLineEdit(self.app_data.get('name', ''))
        self.path_edit = QLineEdit(self.app_data.get('path', ''))
        self.args_edit = QLineEdit(self.app_data.get('args', ''))
        self.working_dir_edit = QLineEdit(self.app_data.get('working_dir', ''))

        self.form_layout.addRow('Name', self.name_edit)
        self.form_layout.addRow('Path', self.path_edit)
        self.form_layout.addRow('Args', self.args_edit)
        self.form_layout.addRow('Working Dir', self.working_dir_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)



