from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton

# # Позиция мыши в момент нажатия
mouse_position_in_image_window = QtCore.QPoint(0, 0)



class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    entered = pyqtSignal()
    leaved = pyqtSignal()
    moved = pyqtSignal()

    def mouseReleaseEvent(self, e):
        if e.button() == 1:
            super().mouseReleaseEvent(e)
            mouse_position_in_image_window.setX(e.pos().x())
            mouse_position_in_image_window.setY(e.pos().y())
            self.clicked.emit()

    def enterEvent(self, e):
        self.entered.emit()

    def leaveEvent(self, e):
        self.leaved.emit()

    def mouseMoveEvent(self, ev):
        self.moved.emit()


class UnfocusedButton(QPushButton):
    def __init__(self, win):
        super().__init__(win)

    def keyPressEvent(self, event):
        pass
