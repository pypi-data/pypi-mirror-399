from PySide6 import QtCore, QtGui, QtWidgets
from .config import cfg
from .ui import finder_ui


class Finder(QtWidgets.QWidget, finder_ui.Ui_Form):
    label_findit = QtCore.Signal(str,bool,bool) # str: find text, bool: is backward,bool is regx
    label_replaceit = QtCore.Signal(str,str,bool,bool) # str: find text, str: replace text, bool: is regx, bool is all
    label_reset = QtCore.Signal()
    finder_closed = QtCore.Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Finder"))
        self.setWindowIcon(QtGui.QIcon("finder.png"))
        # 设置为独立窗口，不置顶，避免遮挡对话框
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, False)

        self.toolButton_fold.setText("\u02c3")
        self.frame_replace.setVisible(False)
        self.folded_expanded_height = [167, 217]
        self.setFixedHeight(self.folded_expanded_height[0])
        self.toolButton_fold.clicked.connect(self.on_toolButton_fold_clicked)
        self.pushButton_find.clicked.connect(self.find_next)
        self.pushButton_find_prev.clicked.connect(self.find_prev)
        self.pushButton_replace.clicked.connect(self.replace)
        self.pushButton_replace_all.clicked.connect(self.replace_all)
        self.pushButton_replace_reset.clicked.connect(self.reset)

    def on_toolButton_fold_clicked(self):
        if self.frame_replace.isVisible():
            # 缩小
            self.frame_replace.setVisible(False)
            self.toolButton_fold.setText("\u02c3")
            target_height = self.folded_expanded_height[0]
        else:
            # 展开
            self.frame_replace.setVisible(True)
            self.toolButton_fold.setText("\u02c5")
            target_height = self.folded_expanded_height[1]
        
        # 延迟调整高度，确保布局管理器完成调整
        QtCore.QTimer.singleShot(0, lambda: self.setFixedHeight(target_height))

    def closeEvent(self, event):
        self.finder_closed.emit()
        super().closeEvent(event)

    def find_next(self):
        text = self.lineEdit_find.text()
        if text:
            self.label_findit.emit(text,False,self.checkBox.isChecked())

    def find_prev(self):
        text = self.lineEdit_find.text()
        if text:
            self.label_findit.emit(text,True,self.checkBox.isChecked())

    def replace(self):
        text = self.lineEdit_find.text()
        if text:
            self.label_replaceit.emit(text,self.lineEdit_replace.text(),self.checkBox.isChecked(),False)

    def replace_all(self):
        text = self.lineEdit_find.text()
        if text:
            self.label_replaceit.emit(text,self.lineEdit_replace.text(),self.checkBox.isChecked(),True)

    def reset(self):
        self.label_reset.emit()