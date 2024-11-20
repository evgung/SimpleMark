import styles
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QDialog
from caution import sendError


class InitWorkWindow(QDialog):

    def __init__(self):
        super().__init__()
        # # Переменные для переноса в основной класс (уже перенесены)
        self.path_to_video = ""  # Путь к видео
        self.path_to_save = ""  # Путь к папке с сохранением
        self.frames_per_second = 0  # Количество кадров в секунду для разбиения
        self.name_of_save_folder = 0  # Название папки, которая будет создана для хранения сохранений
        self.save_width = False
        self.result_width = 800
        # # UI
        self.label_way_to_video_selection = QLabel()
        self.label_way_to_save_selection = QLabel()
        self.box_save_name = QLineEdit()
        self.box_save_name.setAlignment(Qt.AlignCenter)

        int_validator = QtGui.QIntValidator(self)

        self.box_amount_of_frames = QLineEdit()
        self.box_amount_of_frames.setValidator(int_validator)
        self.box_amount_of_frames.setToolTip("Количество кадров, которое будет получено, если это возможно, на 1 секунду видео")
        self.box_amount_of_frames.setAlignment(Qt.AlignCenter)

        self.box_change_to_width = QLineEdit()
        self.box_change_to_width.setDisabled(True)
        self.box_change_to_width.setValidator(int_validator)
        self.box_change_to_width.setToolTip("Ширина полученных кадров")
        self.box_change_to_width.setAlignment(Qt.AlignCenter)

        self.chbox_save_base_width = QtWidgets.QCheckBox("Сохранить исходную ширину")
        self.chbox_save_base_width.clicked.connect(self.reflectField)

        self.is_initialized = False
        self.initUI()

    def reflectField(self):
        self.box_change_to_width.setDisabled(self.chbox_save_base_width.checkState())

    def selectVideo(self):
        fd = QtWidgets.QFileDialog()
        self.path_to_video = fd.getOpenFileName(self, 'Выбрать видео', filter='Видео MP4 (*.mp4)')
        self.label_way_to_video_selection.setText(self.path_to_video[0])

    def selectFolder(self):
        fd = QtWidgets.QFileDialog()
        self.path_to_save = fd.getExistingDirectory(self, 'Выбрать папку')
        print(self.path_to_save)
        self.label_way_to_save_selection.setText(self.path_to_save)

    def submit(self):
        if self.box_amount_of_frames.text() == "" or self.box_save_name.text() == "" or (self.chbox_save_base_width.checkState() and self.box_change_to_width == ""):
            sendError("Данные не указаны или указаны некорректно")
        elif self.path_to_save == "" or self.path_to_video == "":
            sendError("Пути не указаны")
        else:
            self.frames_per_second = int(self.box_amount_of_frames.text())
            self.name_of_save_folder = self.box_save_name.text()
            self.save_width = self.chbox_save_base_width.checkState()
            if self.save_width:
                self.result_width = 0
            else:
                self.result_width = int(self.box_change_to_width.text())
            self.is_initialized = True
            self.close()

    def cancel(self):
        self.close()

    def initUI(self):
        self.setWindowTitle("Открыть")
        self.resize(300, 300)

        self.setStyleSheet(styles.dialog_style)

        label_way_to_video = QLabel("Путь к видео")
        label_way_to_save = QLabel("Путь к папке сохранения")

        btn_select_video = QtWidgets.QPushButton("Выбор видео")
        btn_select_video.setToolTip("Выбрать директорию с видео, кадры которого необходимо разметить")
        btn_select_video.clicked.connect(self.selectVideo)
        btn_select_video.adjustSize()

        btn_select_save = QtWidgets.QPushButton("Выбор папки")
        btn_select_save.setToolTip("Выбрать директорию, в которой необходимо создать папку с сохранениями")
        btn_select_save.clicked.connect(self.selectFolder)
        btn_select_save.adjustSize()

        lbl_save_name = QLabel("Название папки сохранения")
        lbl_amount_of_frames = QLabel("Количество кадров в секунду")
        lbl_change_to_width = QLabel("               Сжать изображение до")

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.cancel)
        btn_cancel.adjustSize()
        btn_confirm = QPushButton("ОК")
        btn_confirm.clicked.connect(self.submit)
        btn_confirm.adjustSize()

        self.reflectField()

        grid = QtWidgets.QGridLayout(self)
        grid.setSpacing(20)
        grid.addWidget(label_way_to_video, 1, 1)
        grid.addWidget(self.label_way_to_video_selection, 1, 3)
        grid.addWidget(btn_select_video, 1, 2)
        grid.addWidget(label_way_to_save, 2, 1)
        grid.addWidget(self.label_way_to_save_selection, 2, 3)
        grid.addWidget(btn_select_save, 2, 2)
        grid.addWidget(lbl_save_name, 3, 1)
        grid.addWidget(self.box_save_name, 3, 2)
        grid.addWidget(lbl_amount_of_frames, 4, 1)
        grid.addWidget(self.box_amount_of_frames, 4, 2)
        grid.addWidget(self.chbox_save_base_width, 6, 1)
        grid.addWidget(lbl_change_to_width, 7, 1)
        grid.addWidget(self.box_change_to_width, 7, 2)
        grid.addWidget(btn_cancel, 8, 2)
        grid.addWidget(btn_confirm, 8, 3)


class OpenOld(QDialog):

    def __init__(self):
        super().__init__()
        self.old_save = ""
        self.initUI()

    def initUI(self):
        fd = QtWidgets.QFileDialog()
        self.old_save = fd.getExistingDirectory()
