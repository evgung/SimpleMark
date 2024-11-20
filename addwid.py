from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton

# # Позиция мыши в момент нажатия
mouse_position_in_image_window = QtCore.QPoint(0, 0)


class ClickableLabel(QLabel):
    clicked = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, e):
        if e.button() == 1:
            super().mouseReleaseEvent(e)
            mouse_position_in_image_window.setX(e.pos().x())
            mouse_position_in_image_window.setY(e.pos().y())
            self.clicked.emit()


class UnfocusedButton(QPushButton):
    def __init__(self, win):
        super().__init__(win)

    def keyPressEvent(self, event):
        pass
