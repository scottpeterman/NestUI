from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QFrame


class CustomLabel(QLabel):
    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super(CustomTitleBar, self).__init__(parent)
        self.mouse_press_pos = None
        self.mouse_release_pos = None
        self.window_move_pos = None

    def mousePressEvent(self, event):
        try:
            self.mouse_press_pos = event.globalPosition().toPoint()  # global
            self.mouse_release_pos = event.globalPosition().toPoint()
            parent_window = self.window()
            if parent_window:
                self.window_move_pos = parent_window.frameGeometry().topLeft() - self.mouse_press_pos
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event):
        try:
            if self.mouse_press_pos:
                parent_window = self.window()
                if parent_window:
                    move_point = event.globalPosition().toPoint()
                    parent_window.move(move_point + self.window_move_pos)
                self.mouse_release_pos = event.globalPosition().toPoint()
        except Exception as e:
            print(e)

    def mouseReleaseEvent(self, event):
        try:
            release_point = event.globalPosition().toPoint()
            if self.mouse_release_pos != self.mouse_press_pos:
                self.mouse_press_pos = None
        except Exception as e:
            print(e)

