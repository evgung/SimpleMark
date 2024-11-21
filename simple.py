# -*- coding: utf-8 -*-
import time
import os
import pyautogui
from threading import Thread
from saver import Saver
from loader import Loader
from point import Point

import marker
import styles
from addwid import ClickableLabel, UnfocusedButton, mouse_position_in_image_window
from caution import WarningWindow
from marker import Mark, undo_stack, redo_stack
import caution
from starting import InitWorkWindow, OpenOld
from vidext import VideoFrameExtractor
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QMenuBar
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
        # self.image_list = []  # список изображений # НЕ АКТУАЛЬНО
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
        self.image_window = ClickableLabel(self)
        self.image_window.setScaledContents(True)
        self.image_window.clicked.connect(self.onClickImage)

        # кнопочки влево/вправо
        button_size = screen_width - self.fr_disp_x - 10 - self.back_width
        previous_button = UnfocusedButton(self)
        previous_button.resize(button_size, button_size)
        previous_button.setIcon(QtGui.QIcon("Images/pointer_left.png"))
        previous_button.setIconSize(QtCore.QSize(button_size, button_size))
        previous_button.move(self.back_width + self.fr_disp_x + 5, self.fr_disp_y - 1)
        previous_button.clicked.connect(self.toPreviousImage)
        previous_button.setShortcut(224)

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

        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("     Файл     ")
        edit_menu = menu_bar.addMenu("     Правка     ")

        new_action = QAction("Новый проект", self)
        new_action.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.startNewProject)

        open_action = QAction("Открыть проект", self)
        open_action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.openOldProject)

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

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        menu_bar.adjustSize()

        self.setFocus()

    # endregion

    # region События

    # # Переопределённые событий
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.toPreviousImage()
        if event.key() == Qt.Key_Right or event.key() == Qt.Key_F:
            self.toNextImage()

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
        else:
            self.image_window.setFixedSize(int(image.width() * mult_x), int(image.height() * mult_x))
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
            return True
        else:
            caution.sendError("Переход на изображение невозможен")
            return False

    # # Осуществление перехода на изображение по номеру при нажатии кнопки "Перейти"
    def clickToNumber(self):
        if self.to_num_image.text() != "":
            self.toImageByNumber(int(self.to_num_image.text()))

    # endregion

    # # Открывает окно для получения информации о новом проекте, сохраняет информацию, если всё нормально
    def startNewProject(self):
        init_work_window = InitWorkWindow()
        init_work_window.exec()
        if init_work_window.is_initialized:
            self.video_path = init_work_window.path_to_video[0]
            self.saves_path = os.path.join(init_work_window.path_to_save, init_work_window.name_of_save_folder)
            self.save_width = init_work_window.save_width
            self.result_width = init_work_window.result_width
            self.frames_per_second = init_work_window.frames_per_second
            self.vfe = VideoFrameExtractor(self.video_path, self.saves_path, self.frames_per_second, self.save_width, self.result_width)
            self.frame_path, self.frame_name = self.vfe.getInfo()
            self.saver = Saver(self.saves_path)
            self.loader = Loader(self.saves_path)
            additional_thread = Thread(target=self.vfe.extract_frames)
            additional_thread.start()
            time.sleep(1 / self.frames_per_second + 2)
            self.toImageByNumber(0)

    # # Предупреждает о возможной потере данных
    def warn(self):
        ww = WarningWindow()
        ww.exec()
        if ww.save_option:
            self.saveProject()
            return True
        elif ww.pofig_option:
            self.close()
            return True
        return False

    # # # Полезные для вас функции

    # # Получает изображение QPixmap по пути
    def getImage(self, path):
        return QPixmap(path)

    # # # Ваша часть(или честь, если хотите)

    # # Инициализация работы, заполнение массива и других переменных
    #def initWork(self, frames_per_second, frames_edit_amount):
        # Здесь frames_per_second - количество кадров в секунду
        # Тут frames_edit_amount - количество кадров размечаемых за заход
        # Неправильно будет хранить в памяти 10000 QPixmap-ов
        #pass


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
            self.toImageByNumber(inf['last_frame_number'])

    # # Сохранение проекта
    def saveProject(self):
        self.saveThis()
        self.saver.saveProject(self.image_number, self.video_path, 0, self.frames_per_second,
                               self.frame_name, self.frame_path)

    def saveThis(self):
        k = self.getPointsList()
        self.saver.saveFramePoints(self.image_number, self.getPointsList())

    def loadThis(self, number):
        l = self.loader.getFramePoints(number)
        print(l)
        for point in l:
            mark = Mark(point.x * self.image_window.width() + self.image_window.x(), point.y * self.image_window.height() + self.image_window.y(), point.width, len(self.marks))
            self.layout().addWidget(mark)
            self.marks.append(mark)

    def getPointsList(self):
        res = []
        for mark in self.marks:
            if mark.is_enabled:
                res.append(Point((mark.pos_x - self.image_window.x()) / self.image_window.width(), (mark.pos_y - self.image_window.y()) / self.image_window.height(), mark.width()))
                print(str(mark.pos_x) + "   " + str(mark.x()))
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
        # обязательно нормализуем, картинка сжата
        norm_x = mouse_position_in_image_window.x() / self.image_window.width()
        norm_y = mouse_position_in_image_window.y() / self.image_window.height()

        mark = Mark(
            mouse_position_in_image_window.x() + self.image_window.x(),
            mouse_position_in_image_window.y() + self.image_window.y(),
            30,
            len(self.marks)
        )

        self.layout().addWidget(mark)
        self.marks.append(mark)
        undo_stack.append(len(self.marks) - 1)
        print("x:", norm_x, "\b,  y: ", norm_y)
