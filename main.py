import os
import sys
import logging

from simple import SimpleMark
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import styles
from PyQt5.QtWinExtras import QtWin


# Логирование для дебага (информация об ошибке выводится в консоль)
def log_exception(exc_type, exc_value, exc_tb):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))


logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
sys.excepthook = log_exception  # Устанавливаем обработчик для всех исключений


if __name__ == '__main__':
    myappid = 'donttouchifworking.simplemark.one.1'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Images/logo.png"))
    sm = SimpleMark()
    sm.setStyleSheet(styles.main_style)
    sm.showMaximized()
    sm.setMarkColorRed()
    sys.exit(app.exec_())
