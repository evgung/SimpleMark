import sys
from simple import SimpleMark
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import styles
from PyQt5.QtWinExtras import QtWin


if __name__ == '__main__':
    myappid = 'donttouchifworking.simplemark.one.1'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Images/logo.png"))
    sm = SimpleMark()
    sm.setStyleSheet(styles.main_style)
    sm.showMaximized()
    sys.exit(app.exec_())
