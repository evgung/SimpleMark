from PyQt5.QtWidgets import QLabel

# # Переменные для отката и повторения
undo_stack = []
redo_stack = []


class Mark(QLabel):

    def __init__(self, disp_x, disp_y, win_x, win_y, size, number, comp_value=1):
        super().__init__()
        self.size = size
        self.resize(
            int(self.size * comp_value),
            int(self.size * comp_value)
        )
        self.disp_x = disp_x  # смещение (координаты поля с кадром)
        self.disp_y = disp_y
        self.win_x = win_x  # позиция метки в окне (не нормализовано)
        self.win_y = win_y
        self.refresh()

        self.number = number
        self.is_enabled = True

    def setWinX(self, win_x):
        self.win_x = win_x
        self.refresh()

    def setWinY(self, win_y):
        self.win_y = win_y
        self.refresh()

    def refresh(self):
        self.move(
            int(self.disp_x + self.win_x - self.width() // 2),
            int(self.disp_y + self.win_y - self.height() // 2)
        )

    def mousePressEvent(self, ev):
        if ev.button() == 2:
            self.setVisible(False)
            self.is_enabled = False
            undo_stack.append(self.number)

    def reflect(self):
        self.is_enabled = not self.is_enabled
        self.setVisible(self.is_enabled)
