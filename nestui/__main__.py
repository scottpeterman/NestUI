import subprocess

from PyQt6.QtCore import QPoint, pyqtProperty
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QFrame, QStackedWidget, QSizePolicy, QMenu
import sys
import yaml
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QSpacerItem
from nestui.Custom_UI import CustomLabel, CustomTitleBar
from ToolboxEditor import ToolboxEditor_UI
class LauncherMenu(QWidget):

    def __init__(self, yaml_path='./toolbox.yaml'):
        super().__init__()
        self.initUI(yaml_path)

    def initUI(self, yaml_path):
        layout = QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        with open(yaml_path, 'r') as stream:
            try:
                yaml_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return

        for group in yaml_data['groups']:
            group_lbl = ClickableLabel(group['name'])
            group_container = QWidget()
            group_layout = QVBoxLayout()
            group_container.setLayout(group_layout)
            group_animation = QPropertyAnimation(group_container, b"maximumHeight")
            group_animation.setEasingCurve(QEasingCurve.Type.Linear)
            group_lbl.mousePressEvent = lambda event, container=group_container, animation=group_animation: self.toggleGroup(container, animation)

            for app in group['apps']:
                app_btn = QPushButton(f"  {app['name']}")
                app_btn.setFlat(True)
                # Store custom properties
                app_btn.setProperty("path", app['path'])
                app_btn.setProperty("args", app['args'])
                app_btn.setProperty("working_dir", app['working_dir'])

                # Connect to custom slot
                app_btn.clicked.connect(self.launch_app_custom)
                group_layout.addWidget(app_btn)

            layout.addWidget(group_lbl)
            layout.addWidget(group_container)

            # Start with groups expanded, uncomment to change default
            # group_container.setMaximumHeight(0)

        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("""
            QPushButton {
                background-color: #292929;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.setFixedWidth(150)


    def toggleGroup(self, container, animation):
        if container.maximumHeight() == 0:
            animation.stop()
            animation.setStartValue(0)
            animation.setEndValue(container.sizeHint().height())
            animation.start()
        else:
            animation.stop()
            animation.setStartValue(container.maximumHeight())
            animation.setEndValue(0)
            animation.start()

    def launch_app(self, path, args, working_dir):
        print(f"Launching App: {path}")
        subprocess.Popen([path] + args.split(), cwd=working_dir, shell=True)

    def launch_app_custom(self):
        button = self.sender()
        path = button.property("path")
        args = button.property("args")
        working_dir = button.property("working_dir")
        self.launch_app(path=path, args=args, working_dir=working_dir)


class ClickableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


class ToolboxUI(QWidget):
    def __init__(self):
        super().__init__()

        # Hide title bar
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.resize_grip = False
        self.old_pos = None
        self.initUI()

    def mousePressEvent(self, event):
        try:
            if event.pos().x() > self.width() - 20 and event.pos().y() > self.height() - 20:
                self.resize_grip = True
                self.old_pos = event.globalPosition().toPoint()  # Use globalPosition().toPoint() in PyQt6
            else:
                self.resize_grip = False
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event):
        if self.resize_grip:
            try:
                delta = QPoint(
                    event.globalPosition().toPoint() - self.old_pos)  # Use globalPosition().toPoint() in PyQt6
                self.resize(self.width() + delta.x(), self.height() + delta.y())
                self.old_pos = event.globalPosition().toPoint()  # Use globalPosition().toPoint() in PyQt6
            except Exception as e:
                print(e)

    def initUI(self):
        self.setWindowTitle('Custom UI')

        self.layout_main = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_content = QHBoxLayout()


        self.top_bar = CustomTitleBar(self)
        self.top_bar.setStyleSheet("padding: 1px;")
        self.top_bar.setStyleSheet("background-color: 292929;")
        self.top_bar.setFixedHeight(40)

        # 1. Create the QMenu for the button
        self.menu = QMenu(self)

        # 2. Add an action to the menu
        edit_toolbox_action = QAction("Edit Toolbox", self)
        edit_toolbox_action.triggered.connect(self.edit_toolbox_method)  # Connect to your desired method
        self.menu.addAction(edit_toolbox_action)


        # Minimize button
        self.btn_minimize = QPushButton("—")
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_minimize.setFlat(True)
        # self.btn_minimize.setFixedWidth(40)
        self.btn_minimize.setMaximumWidth(10)



        self.btn_ellipsis = QPushButton("⋮")
        self.btn_ellipsis.setFlat(True)
        # self.btn_ellipsis.clicked.connect(self.some_method)
        self.btn_minimize.setMaximumWidth(10)
        self.btn_ellipsis.setVisible(True)
        self.btn_ellipsis.clicked.connect(self.show_menu)

        # Close button
        self.btn_close = QPushButton("X")
        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.setMaximumWidth(10)
        self.btn_close.setFlat(True)

        self.btn_minimize.setStyleSheet("padding: 1px;")  # Adjust the value as necessary
        self.btn_ellipsis.setStyleSheet("padding: 1px;")  # Adjust the value as necessary
        self.btn_close.setStyleSheet("padding: 1px;")  # Adjust the value as necessary
        self.btn_minimize.setStyleSheet("QPushButton { margin: 1px; }")
        self.btn_ellipsis.setStyleSheet("QPushButton { margin: 1px; }")
        self.btn_close.setStyleSheet("QPushButton { margin: 1px; }")

        # layout_top.addWidget(self.btn_hamburger)  # Add hamburger button to layout
        layout_top.addWidget(QLabel("NEST"))
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout_top.addItem(spacer)

        layout_top.addWidget(self.btn_ellipsis)
        layout_top.addWidget(self.btn_minimize)
        # layout_top.addWidget(self.btn_restore)
        layout_top.addWidget(self.btn_close)
        layout_top.setContentsMargins(0,0,0,0)
        self.top_bar.setLayout(layout_top)
        self.top_bar.setContentsMargins(0,0,0,0)

        # Left navigation (using the new LauncherMenu class)
        self.left_nav = LauncherMenu()
        # self.left_nav.changePage.connect(self.changePage)  # connect to the new signal


        # Stacked Widget
        self.stacked_widget = QStackedWidget()

        # Combine everything
        layout_content.addWidget(self.left_nav)
        # layout_content.addWidget(self.main_content)
        self.layout_main.addWidget(self.top_bar)
        self.layout_main.addLayout(layout_content)

        self.bottom_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.resize_label = CustomLabel(self)
        pixmap = QPixmap("./nestui/icons/resize-handle.png")
        scaled_pixmap = pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        self.resize_label.setPixmap(scaled_pixmap)
        self.bottom_layout = QHBoxLayout()

        self.bottom_layout.addSpacerItem(self.bottom_spacer)
        self.bottom_layout.addWidget(self.resize_label)
        self.layout_main.addLayout(self.bottom_layout)
        self.setLayout(self.layout_main)

    def restoreWindow(self):
        print("Restoring window...")

        print("Window should be restored.")

    def edit_toolbox_method(self):
        print(f"Opening toolbox yaml editor")
        self.dlg = ToolboxEditor_UI()
        self.dlg.show()
        pass

    def show_menu(self):
        # The menu will be shown where the mouse cursor is.
        self.menu.exec(QCursor.pos())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app.setStyle("Fusion")
#
#     main = ToolboxUI()
#     main.show()
#
#
#     sys.exit(app.exec())
