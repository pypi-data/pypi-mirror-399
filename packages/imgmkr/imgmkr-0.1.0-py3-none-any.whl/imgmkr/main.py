from PySide6 import QtWidgets, QtGui, QtCore
from .mainwindow import MainWindow


def main():
    app = QtWidgets.QApplication()
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
