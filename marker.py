from PyQt5.QtWidgets import QLabel

# # Переменные для отката и повторения
undo_stack = []
redo_stack = []

def unre_inf():
    print("---------------")
    print("undo: ", undo_stack)
    print("redo: ", redo_stack)

class Mark(QLabel):

    def __init__(self, pos_x, pos_y, size, number, comp_value=1):
        super().__init__()
        self.setStyleSheet("border: 1px solid red; background-color: rgba(255, 0, 0, 50)")
        self.size = size
        self.move(pos_x - (size * comp_value) // 2, pos_y - (size * comp_value) // 2)
        self.resize(self.size * comp_value, self.size * comp_value)

        self.number = number
        self.pos_x = pos_x  # позиция в окне
        self.pos_y = pos_y  # она не нормализована
        self.is_enabled = True

    def mousePressEvent(self, ev):
        if ev.button() == 2:
            self.setVisible(False)
            self.is_enabled = False
            undo_stack.append(self.number)
            unre_inf()

    def reflect(self):
        self.is_enabled = not self.is_enabled
        self.setVisible(self.is_enabled)
