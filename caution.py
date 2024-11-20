from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
import styles


class ErrorWindow(QDialog):

    def __init__(self, et):
        super().__init__()
        self.initUI(et)

    def initUI(self, et):
        self.setStyleSheet(styles.error_style)
        self.setWindowTitle("Сообщение об ошибке")
        error_label = QLabel(et, self)
        error_label.move(20, 20)
        error_label.adjustSize()
        self.adjustSize()


class WarningWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.save_option = False
        self.pofig_option = False
        self.initUI()

    def pofigClicked(self):
        self.pofig_option = True
        self.close()

    def submitClicked(self):
        self.save_option = True
        self.close()

    def initUI(self):
        self.setWindowTitle("Предупреждение")
        self.setStyleSheet(styles.dialog_style)
        lbl_warn_1 = QLabel("Если данные не были сохранены, то они будут утеряны")
        lbl_warn_2 = QLabel("В программе нет автосохранения")
        btn_cancel = QPushButton("Отмена")
        btn_submit = QPushButton("Сохранить")
        btn_pofig = QPushButton("Выйти, не сохраняя")
        common_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.Down)
        self.setLayout(common_layout)
        common_layout.setSpacing(15)
        common_layout.addWidget(lbl_warn_1)
        common_layout.addWidget(lbl_warn_2)
        common_layout.addWidget(btn_submit)
        common_layout.addWidget(btn_cancel)
        common_layout.addWidget(btn_pofig)
        btn_pofig.setStyleSheet("color: red")
        btn_pofig.clicked.connect(self.pofigClicked)
        btn_submit.clicked.connect(self.submitClicked)
        btn_cancel.clicked.connect(self.close)


def sendError(error_text):
    error_window = ErrorWindow(error_text)
    error_window.exec()
