# -*- coding: utf-8 -*-
import time
import os
from distutils.core import setup_keywords

import pyautogui
from threading import Thread
from saver import Saver
from loader import Loader
from point import Point

import marker
import styles
from addwid import ClickableLabel, UnfocusedButton, mouse_position_in_image_window
from caution import WarningWindow, ErrorWindow
from marker import Mark, undo_stack, redo_stack
import caution
from starting import InitWorkWindow, OpenOld
from vidext import VideoFrameExtractor
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QInputEvent
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QMenuBar, QPushButton
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt


class SimpleMark(QMainWindow):

    # region Инициализация
    def __init__(self):
        super().__init__()
        # # UI
        self.image_window = QLabel()  # окно для изображения
        self.to_num_image = QLineEdit(self)  # поле для ввода номера
        self.back_width = 0  # ширина и высота рамки с изображением
        self.back_height = 0  # именно РАМКИ А НЕ ИЗОБРАЖЕНИЯ
        self.fr_disp_x = 10  # сдвиг рамки относительно окна
        self.fr_disp_y = 30

        # # Полезные вам параметры (новые параметры добавлять сюда же)
        self.video_path = ""  # путь к видео
        self.saves_path = ""  # путь сохранения
        self.vfe = 0  # экстрактор видео
        self.video_name = ""  # отдельно название видео

        # # Updated
        self.frames_per_second = 10  # количество кадров забираемых в секунду (если это возможно)
        self.save_width = False  # сохранить исходную ширину?
        self.result_width = 800  # если save_width = False, то меняет ширину на выбранную
        self.marks = []

        # # Переменные для получения изображений
        self.frame_path = ""  # путь к изображению с его названием (без номера)
        self.frame_name = ""  # общая часть названия изображения
        # self.frames_amount = 0  # количество изображений
        self.image_number = -1  # номер текущего изображения
        # таким образом имеем список изображений

        self.saver = Saver("")
        self.loader = Loader("")
        self.markWidth = 30
        self.markWidthBox = QLineEdit(self)
        self.moreWidButton = QPushButton(self)
        self.lessWidButton = QPushButton(self)
        self.compressionValue = 1

        # количество кадров
        self.number_box = QLabel(self)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Simple Mark")

        screen_width, screen_height = pyautogui.size()
        screen_height *= 0.98
        self.resize(int(screen_width), int(screen_height))

        # размеры экрана изображения (если что это для границ изображения)
        # хотя по факту это просто другой лабель
        self.back_width = int(0.88 * self.width())
        self.back_height = int((self.height() - self.fr_disp_y) * 0.94)

        # Задний ограничитель
        background_label = QLabel(self)
        background_label.setStyleSheet(styles.background_field_style)
        background_label.move(self.fr_disp_x, self.fr_disp_y)
        background_label.setFixedSize(self.back_width, self.back_height)
        background_label.setFrameShape(QtWidgets.QFrame.Box)
        background_label.setStyleSheet("border: 1px solid black; background-color: white;")
        self.image_window = ClickableLabel()
        self.image_window.setScaledContents(True)
        self.image_window.clicked.connect(self.onClickImage)
        self.image_window.setStyleSheet("border: 1px dashed black;")

        # кнопочки влево/вправо
        button_size = screen_width - self.fr_disp_x - 10 - self.back_width
        previous_button = UnfocusedButton(self)
        previous_button.resize(button_size, button_size)
        previous_button.setIcon(QtGui.QIcon("Images/pointer_left.png"))
        previous_button.setIconSize(QtCore.QSize(button_size, button_size))
        previous_button.move(self.back_width + self.fr_disp_x + 5, self.fr_disp_y - 1)
        previous_button.clicked.connect(self.toPreviousImage)
        previous_button.setShortcut(224)

        self.number_box.move(self.back_width + self.fr_disp_x + 5, self.height() - 100)
        self.number_box.resize(button_size, 40)
        self.number_box.setAlignment(Qt.AlignCenter)
        self.number_box.setStyleSheet("font-family: 'arial'; font-size: 18px; color: grey; border: none;")

        next_button = UnfocusedButton(self)
        next_button.resize(button_size, button_size)
        next_button.setIcon(QtGui.QIcon("Images/pointer_right.png"))
        next_button.setIconSize(QtCore.QSize(button_size, button_size))
        next_button.move(self.back_width + self.fr_disp_x + 5, self.fr_disp_y + 3 + button_size)
        next_button.clicked.connect(self.toNextImage)

        # поле для номера изображения
        self.to_num_image.resize(button_size, 40)
        self.to_num_image.move(self.back_width + self.fr_disp_x + 5, 2 * button_size + self.fr_disp_y + 6)
        self.to_num_image.setAlignment(Qt.AlignCenter)
        self.to_num_image.setPlaceholderText("Номер изображения")
        int_validator = QtGui.QIntValidator(self)
        self.to_num_image.setValidator(int_validator)
        # кнопочка для перехода по номеру
        btn_num_image = UnfocusedButton(self)
        btn_num_image.resize(button_size, 40)
        btn_num_image.move(self.back_width + self.fr_disp_x + 5, 2 * button_size + self.fr_disp_y + 49)
        btn_num_image.setText("Перейти")
        btn_num_image.clicked.connect(self.clickToNumber)

        lblWidth = QLabel(self)
        lblWidth.resize(button_size, 40)
        lblWidth.move(self.back_width + self.fr_disp_x + 5, 2 * button_size + self.fr_disp_y + 93)
        lblWidth.setText('Ширина разметки')
        lblWidth.setAlignment(Qt.AlignCenter)

        self.markWidthBox.resize(int(0.7 * button_size), 40)
        self.markWidthBox.move(self.back_width + self.fr_disp_x + 5, 2 * button_size + self.fr_disp_y + 138)
        self.markWidthBox.setAlignment(Qt.AlignCenter)
        self.markWidthBox.setPlaceholderText("Ширина")
        self.markWidthBox.setValidator(int_validator)
        self.markWidthBox.setMaxLength(3)

        self.moreWidButton.resize(int(0.25 * button_size), 19)
        self.moreWidButton.move(
            int(self.back_width + self.fr_disp_x + 5 + 0.75 * button_size),
            int(2 * button_size + self.fr_disp_y + 138)
        )
        self.moreWidButton.clicked.connect(self.addWidth)
        self.moreWidButton.setIcon(QtGui.QIcon("Images/more.png"))
        self.lessWidButton.resize(int(0.25 * button_size), 19)
        self.lessWidButton.move(
            int(self.back_width + self.fr_disp_x + 5 + 0.75 * button_size),
            int(2 * button_size + self.fr_disp_y + 158)
        )
        self.lessWidButton.clicked.connect(self.takeWidth)
        self.lessWidButton.setIcon(QtGui.QIcon("Images/less.png"))

        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("     Файл     ")
        edit_menu = menu_bar.addMenu("     Правка     ")
        color_menu = menu_bar.addMenu("     Цвет меток     ")
        tools_menu = menu_bar.addMenu("     Инструменты     ")

        new_action = QAction("Новый проект", self)
        new_action.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.startNewProject)

        open_action = QAction("Открыть проект", self)
        open_action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.openOldProject)

        fin_action = QAction("Собрать датасет", self)
        # open_action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        fin_action.triggered.connect(self.finalize)

        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.saveProject)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)

        undo_action = QAction("Отменить", self)
        undo_action.setShortcut(QtGui.QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.undo)

        redo_action = QAction("Повторить", self)
        redo_action.setShortcut(QtGui.QKeySequence("Ctrl+Y"))
        redo_action.triggered.connect(self.redo)

        setred_action = QAction("Красный", self)
        setred_action.triggered.connect(lambda: self.setMarkColor(255, 0, 0))

        setgreen_action = QAction("Зелёный", self)
        setgreen_action.triggered.connect(lambda: self.setMarkColor(0, 255, 0))

        setyellow_action = QAction("Жёлтый", self)
        setyellow_action.triggered.connect(lambda: self.setMarkColor(255, 255, 0))

        setblue_action = QAction("Синий", self)
        setblue_action.triggered.connect(lambda: self.setMarkColor(0, 0, 255))

        setblack_action = QAction("Чёрный", self)
        setblack_action.triggered.connect(lambda: self.setMarkColor(0, 0, 0))

        setwhite_action = QAction("Белый", self)
        setwhite_action.triggered.connect(lambda: self.setMarkColor(255, 255, 255))

        setfuchsia_action = QAction("Фуксия", self)
        setfuchsia_action.triggered.connect(lambda: self.setMarkColor(255, 0, 255))

        setaqua_action = QAction("Аква", self)
        setaqua_action.triggered.connect(lambda: self.setMarkColor(0, 255, 255))

        setspec_action = QAction("Выбрать...", self)
        setspec_action.triggered.connect(self.selectColor)

        change_action = QAction("Выравнивание размера", self)
        change_action.triggered.connect(self.openMarkSizeField)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(fin_action)
        file_menu.addAction(exit_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        color_menu.addAction(setred_action)
        color_menu.addAction(setblue_action)
        color_menu.addAction(setgreen_action)
        color_menu.addAction(setyellow_action)
        color_menu.addAction(setblack_action)
        color_menu.addAction(setwhite_action)
        color_menu.addAction(setfuchsia_action)
        color_menu.addAction(setaqua_action)
        color_menu.addAction(setspec_action)
        tools_menu.addAction(change_action)
        menu_bar.adjustSize()

        self.setFocus()

    def addWidth(self):
        self.markWidthBox.setText(str(int(self.markWidthBox.text()) + 2))

    def takeWidth(self):
        self.markWidthBox.setText(str(int(self.markWidthBox.text()) - 2))
    # endregion

    # region События

    # # Переопределённые событий
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.toPreviousImage()
        if event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.toNextImage()
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.addWidth()
        if event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.takeWidth()

    def mouseReleaseEvent(self, event):
        self.setFocus()

    def closeEvent(self, event):
        if not self.warn():
            event.ignore()

    # endregion

    # region Работа с кадром

    # # # UI

    # # Эта функция кладёт изображение в окно, формат изображения QPixmap
    def setImage(self, image):
        mult_x = self.back_width / image.width()
        mult_y = self.back_height / image.height()
        if mult_x > mult_y:
            self.image_window.setFixedSize(int(image.width() * mult_y), int(image.height() * mult_y))
            self.compressionValue = mult_y
        else:
            self.image_window.setFixedSize(int(image.width() * mult_x), int(image.height() * mult_x))
            self.compressionValue = mult_x
        self.image_window.setPixmap(image)
        if mult_x > mult_y:
            image_window_width = int((self.back_width - self.image_window.width()) / 2 + self.fr_disp_x)
            self.image_window.move(image_window_width, self.fr_disp_y)
        else:
            image_window_height = int((self.back_height - self.image_window.height()) / 2 + self.fr_disp_y)
            self.image_window.move(self.fr_disp_x, image_window_height)
        self.image_window.setFrameShape(QtWidgets.QFrame.Box)

    # # Переход на предыдущий кадр
    def toPreviousImage(self):
        self.toImageByNumber(self.image_number - 1)
        self.setFocus()

    # # Переход на следующий кадр
    def toNextImage(self):
        self.toImageByNumber(self.image_number + 1)
        self.setFocus()

    # # Переход на изображение под номером number
    def toImageByNumber(self, number):
        if self.image_number != -1:
            self.saveThis()
        if os.path.exists(self.frame_path + str(number) + '.png'):
            self.image_number = number
            self.setImage(self.getImage((self.frame_path + str(self.image_number) + '.png')))
            undo_stack.clear()
            redo_stack.clear()
            for element in self.marks:
                element.setParent(None)
                element.deleteLater()
            self.marks.clear()
            self.loadThis(number)
            self.number_box.setText('№ ' + str(number))
            return True
        else:
            caution.sendError("Переход на изображение невозможен")
            return False

    # # Осуществление перехода на изображение по номеру при нажатии кнопки "Перейти"
    def clickToNumber(self):
        if self.to_num_image.text() != "":
            self.toImageByNumber(int(self.to_num_image.text()))
        self.setFocus(True)

    # endregion

    # # Открывает окно для получения информации о новом проекте, сохраняет информацию, если всё нормально
    def startNewProject(self):
        init_work_window = InitWorkWindow()
        init_work_window.exec()
        if init_work_window.is_initialized:
            self.video_path = init_work_window.path_to_video
            self.saves_path = os.path.join(init_work_window.path_to_save, init_work_window.name_of_save_folder)
            self.save_width = init_work_window.save_width
            self.result_width = init_work_window.result_width
            self.frames_per_second = init_work_window.frames_per_second
            self.vfe = VideoFrameExtractor(self.video_path, self.saves_path, self.frames_per_second, self.save_width, self.result_width)
            self.frame_path, self.frame_name = self.vfe.getInfo()
            self.saver = Saver(self.saves_path)
            self.loader = Loader(self.saves_path)
            self.markWidthBox.setText('30')
            additional_thread = Thread(target=self.vfe.extract_frames)
            additional_thread.start()
            time.sleep(1 / self.frames_per_second + 2)
            self.layout().addWidget(self.image_window)
            self.toImageByNumber(0)
            self.saveProject()
        init_work_window.deleteLater()

    # # Предупреждает о возможной потере данных
    def warn(self):
        ww = WarningWindow()
        ww.exec()
        if ww.save_option:
            self.saveProject()
            ww.deleteLater()
            return True
        elif ww.pofig_option:
            self.close()
            ww.deleteLater()
            return True
        ww.deleteLater()
        return False

    # # # Полезные для вас функции

    # # Получает изображение QPixmap по пути
    def getImage(self, path):
        return QPixmap(path)

    # # # Ваша часть

    # # Открытие старого проекта
    def openOldProject(self):
        open_old = OpenOld()
        self.saves_path = open_old.old_save
        if open_old.old_save != '':
            self.saver = Saver(self.saves_path)
            self.loader = Loader(self.saves_path)
            inf = self.loader.getProjectProperties()
            self.frames_per_second = inf['fps']
            self.frame_name = inf['image_name']
            self.frame_path = inf['image_path']
            if 'mark_width' in inf.keys():
                self.markWidth = inf['mark_width']
            else:
                self.markWidth = 30
            self.markWidthBox.setText(str(self.markWidth))
            self.layout().addWidget(self.image_window)
            self.toImageByNumber(inf['last_frame_number'])

    # # Сохранение проекта
    def saveProject(self):
        self.saveThis()
        self.saver.saveProject(self.image_number, self.video_path, 0, self.frames_per_second,
                               self.frame_name, self.frame_path, self.markWidth)

    def saveThis(self):
        self.saver.saveFramePoints(self.image_number, self.getPointsList())

    def loadThis(self, number):
        l = self.loader.getFramePoints(number)
        for point in l:
            mark = Mark(
                int(self.image_window.x()),
                int(self.image_window.y()),
                int(point.x * self.image_window.width()),
                int(point.y * self.image_window.height()),
                point.width,
                len(self.marks),
                self.compressionValue
            )
            self.layout().addWidget(mark)
            self.marks.append(mark)

    def finalize(self):
        self.saveProject()
        self.saver.saveDataset(self.frame_path)

    def getPointsList(self):
        res = []
        for mark in self.marks:
            if mark.is_enabled:
                res.append(Point(
                    mark.win_x / self.image_window.width(),
                    mark.win_y / self.image_window.height(),
                    mark.size))
        return res

    # region Отмена/Возврат

    # # Откат предыдущего действия
    def undo(self):
        if len(undo_stack) > 0:
            m = undo_stack.pop()
            self.marks[m].reflect()
            redo_stack.append(m)

    # # Повторение отменённого действия
    def redo(self):
        if len(redo_stack) > 0:
            m = redo_stack.pop()
            self.marks[m].reflect()
            undo_stack.append(m)

    # endregion

    # # Нажатие на область рисунка (да только рисунка не рамки, можно и рамки сделать только смысла нет)
    # # Всё, что происходит в момент нажатия на поле
    def onClickImage(self):
        self.markWidth = int(self.markWidthBox.text())

        mark = self.setMark(mouse_position_in_image_window.x(),
            mouse_position_in_image_window.y(), self.markWidth)

        self.layout().addWidget(mark)
        self.marks.append(mark)
        undo_stack.append(len(self.marks) - 1)

    def setMark(self, x, y, wid):
        mark = Mark(
            self.image_window.x(),
            self.image_window.y(),
            x,
            y,
            wid,
            len(self.marks),
            self.compressionValue)

        if mark.x() < self.image_window.x():
            mark.setWinX(mark.width() // 2 + 1)
        if mark.y() < self.image_window.y():
            mark.setWinY(mark.height() // 2 + 1)
        if mark.x() + mark.width() > self.image_window.width() + self.image_window.x():
            mark.setWinX(self.image_window.width() - mark.width() // 2 - 1)
        if mark.y() + mark.height() > self.image_window.height() + self.image_window.y():
            mark.setWinY(self.image_window.height() - mark.height() // 2 - 1)
        return mark

    def setMarkColor(self, r, g, b):
        style = (f"Mark {{ border: 1px solid rgb({r}, {g}, {b}); background-color: rgba({r}, {g}, {b}, 50)}} "
                 f"Mark:hover {{background-color: rgba({r}, {g}, {b}, 100);}}")
        self.setStyleSheet(styles.main_style + style)

    def selectColor(self):
        color_d = QtWidgets.QColorDialog()
        col = color_d.getColor()
        self.setMarkColor(col.red(), col.green(), col.blue())

    def openMarkSizeField(self):
        field = QtWidgets.QInputDialog()
        field.exec()
        if (field.textValue().isdigit()):
            self.changeAllMarksSizeTo(int(field.textValue()))
        else:
            error = ErrorWindow("Значение указано некорректно")
            error.exec()
            error.deleteLater()
        field.deleteLater()

    def changeAllMarksSizeTo(self, new_size):
        self.saveThis()
        for way, dir, frames in os.walk(os.path.join(self.saves_path, "info")):
            for frame in frames:
                points = self.loader.getFramePoints(frame)
                res = []
                for point in points:
                    res.append(self.setMark(point.x * self.image_window.width(),
                                            point.y * self.image_window.height(),
                                            new_size))
                pts = []
                for r in res:
                    pts.append(Point(r.win_x / self.image_window.width(), r.win_y / self.image_window.height(), new_size))
                self.saver.saveFramePoints(frame, pts)
                for mark in res:
                    mark.deleteLater()
        for i in range(len(self.marks)):
            self.marks[i].setParent(None)
            self.marks[i].deleteLater()
        self.marks = []
        self.loadThis(self.image_number)
        self.markWidthBox.setText(str(new_size))
