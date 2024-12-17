from PyQt5.QtWidgets import QLabel

# # Переменные для отката и повторения
undo_stack = []
redo_stack = []


class Mark(QLabel):

    def __init__(self, pos_x, pos_y, size, number, comp_value=1):
        super().__init__()
        self.size = size
        self.moveTo(pos_x, pos_y, size * comp_value, size * comp_value)
        self.resize(
            int(self.size * comp_value),
            int(self.size * comp_value)
        )

        self.number = number
        self.pos_x = pos_x  # позиция в окне
        self.pos_y = pos_y  # она не нормализована
        self.is_enabled = True

    def setPosX(self, pos_x):
        self.pos_x = pos_x
        self.moveTo(self.pos_x, self.pos_y, self.width(), self.height())

    def setPosY(self, pos_y):
        self.pos_y = pos_y
        self.moveTo(self.pos_x, self.pos_y, self.width(), self.height())

    def moveTo(self, x, y, width, height):
        self.move(
            int(x - width // 2),
            int(y - height // 2)
        )

    def mousePressEvent(self, ev):
        if ev.button() == 2:
            self.setVisible(False)
            self.is_enabled = False
            undo_stack.append(self.number)

    def reflect(self):
        self.is_enabled = not self.is_enabled
        self.setVisible(self.is_enabled)
