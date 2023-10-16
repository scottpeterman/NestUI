import copy

import yaml
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton,
                             QVBoxLayout, QWidget, QLineEdit, QFormLayout, QMainWindow, QFileDialog, QInputDialog,
                             QMessageBox, QDialog, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication
import sys

from PyQt6.uic.properties import QtWidgets

from EditApp import AppEditDialog



class ToolboxEditor_UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Toolbox Editor")
        self.yaml_dict = None
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels(['Group / Apps'])

        self.new_group_btn = QPushButton("New Group")
        self.new_group_btn.clicked.connect(self.new_group)



        layout = QVBoxLayout()
        layout.addWidget(self.new_group_btn)
        layout.addWidget(self.tree_widget)
        # layout.addLayout(self.form_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # File menu for loading/saving YAML files
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        openFile = QAction('Open', self)
        openFile.triggered.connect(self.load_yaml_file)
        saveFile = QAction('Save', self)
        saveFile.triggered.connect(self.save_yaml_file)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        self.tree_widget.itemDoubleClicked.connect(self.edit_app)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.load_default_yaml()

    def load_default_yaml(self):
        default_file = "toolbox.yaml"
        try:
            with open(default_file, 'r') as f:
                self.yaml_dict = yaml.safe_load(f)
                self.load_tree_from_yaml(self.yaml_dict)
        except FileNotFoundError:
            # Handle the case where the file is not found.
            pass
        except yaml.YAMLError as e:
            # Handle other YAML errors.
            QMessageBox.critical(self, 'YAML Error', f'Error loading default YAML file: {e}')

    def show_context_menu(self, point):
        item = self.tree_widget.itemAt(point)
        if not item:
            return
        try:
            context_menu = QMenu(self)
            if item.parent() is None:  # This is a group
                new_app_action = context_menu.addAction("New App")
                new_app_action.triggered.connect(lambda: self.new_app(item))
                delete_group_action = context_menu.addAction("Delete")
                delete_group_action.triggered.connect(lambda: self.delete_group(item))
            else:  # This is an app
                delete_app_action = context_menu.addAction("Delete")
                delete_app_action.triggered.connect(lambda: self.delete_app(item))

            context_menu.exec(self.tree_widget.mapToGlobal(point))
        except Exception as e:
            print(e)

    def delete_group(self, group_item):
        group_data = group_item.data(0, Qt.ItemDataRole.UserRole)
        self.yaml_dict['groups'].remove(group_data)
        index = self.tree_widget.indexOfTopLevelItem(group_item)
        self.tree_widget.takeTopLevelItem(index)

    def new_app(self, group_item):
        group_data = group_item.data(0, Qt.ItemDataRole.UserRole)
        app_name, ok = QInputDialog.getText(self, 'New App', 'Enter app name:')
        if ok and app_name:
            new_app = {'name': app_name, 'path': '', 'args': '', 'working_dir': ''}
            group_data.setdefault('apps', []).append(new_app)

            # Add to tree
            app_item = QTreeWidgetItem(group_item)
            app_item.setText(0, new_app['name'])
            app_item.setData(0, Qt.ItemDataRole.UserRole, new_app)

    def delete_app(self, app_item):
        app_data = app_item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = app_item.parent()
        parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)

        # Remove from parent data (i.e., group data)
        parent_data['apps'] = [app for app in parent_data['apps'] if app != app_data]

        # Remove from tree
        index = parent_item.indexOfChild(app_item)
        parent_item.takeChild(index)

    def edit_app(self, item):
        app_data = item.data(0, Qt.ItemDataRole.UserRole)
        if app_data:  # Make sure it's an app item
            dialog = AppEditDialog(app_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = {
                    'name': dialog.name_edit.text(),
                    'path': dialog.path_edit.text(),
                    'args': dialog.args_edit.text(),
                    'working_dir': dialog.working_dir_edit.text()
                }

                # Update the item in the tree widget
                item.setData(0, Qt.ItemDataRole.UserRole, updated_data)
                item.setText(0, updated_data['name'])

                # Also update the yaml_dict with this new data
                parent = item.parent()
                parent_data = parent.data(0, Qt.ItemDataRole.UserRole)
                index = parent.indexOfChild(item)
                parent_data['apps'][index] = updated_data

    def new_group(self):
        if self.yaml_dict is None:
            choice = QMessageBox.question(self, 'No YAML Loaded',
                                          "Would you like to create a new YAML file?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if choice == QMessageBox.StandardButton.Yes:
                self.yaml_dict = {'groups': []}
            else:
                return

        group_name, ok = QInputDialog.getText(self, 'New Group', 'Enter group name:')
        if ok and group_name:  # Check that 'Ok' was pressed and a name was provided
            new_group = {'name': group_name, 'apps': []}
            self.yaml_dict.setdefault('groups', []).append(new_group)

            # Add to tree
            group_item = QTreeWidgetItem(self.tree_widget)
            group_item.setText(0, new_group['name'])
            group_item.setData(0, Qt.ItemDataRole.UserRole, new_group)

    def load_yaml_file(self):

        filePath, _ = QFileDialog.getOpenFileName(self, "Open YAML File", "", "YAML Files (*.yaml *.yml);;All Files (*)",)
        if filePath:
            with open(filePath, 'r') as f:
                self.yaml_dict = yaml.safe_load(f)
                self.load_tree_from_yaml(self.yaml_dict)

    def save_yaml_file(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save YAML File", "",
                                                  "YAML Files (*.yaml *.yml);;All Files (*)")
        if filePath:
            new_yaml_dict = {'groups': []}
            root = self.tree_widget.invisibleRootItem()
            for index in range(root.childCount()):
                group_item = root.child(index)
                group_data = group_item.data(0, Qt.ItemDataRole.UserRole)
                apps = []
                for app_index in range(group_item.childCount()):
                    app_item = group_item.child(app_index)
                    app_data = app_item.data(0, Qt.ItemDataRole.UserRole)
                    apps.append(app_data)
                group_data['apps'] = apps
                new_yaml_dict['groups'].append(group_data)

            with open(filePath, 'w') as f:
                yaml.dump(new_yaml_dict, f)

    def load_tree_from_yaml(self, yaml_dict):
        self.tree_widget.clear()
        for group in yaml_dict.get('groups', []):
            group_item = QTreeWidgetItem(self.tree_widget)
            group_item.setText(0, group['name'])
            group_item.setData(0, Qt.ItemDataRole.UserRole, group)
            for app in group['apps']:
                app_item = QTreeWidgetItem(group_item)
                # app_item.refBinding = copy.deepcopy(app)
                app_item.setText(0, app['name'])
                app_item.setData(0, Qt.ItemDataRole.UserRole, app)
        self.tree_widget.expandAll()

    # Implement methods for creating, updating, and deleting groups/apps here

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    ex = ToolboxEditor_UI()
    ex.show()
    sys.exit(app.exec())
