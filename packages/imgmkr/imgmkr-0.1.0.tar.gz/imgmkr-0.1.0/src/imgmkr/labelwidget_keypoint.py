from PySide6 import QtCore, QtGui, QtWidgets
from .config import cfg
from .ui import label_keypoint_ui
from .shape import Shape
from . import utils
import json


class LabelWidgetKeypoint(QtWidgets.QWidget, label_keypoint_ui.Ui_Form):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_confirm.clicked.connect(self.accept)
        self.pushButton_cancle.clicked.connect(self.reject)
        self.annotation_id = -1
        self._history = cfg.getKeypointHistory()
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.itemDoubleClicked.connect(self._onItemDoubleClicked)
        self.setListView()

    def setListView(self):
        self.listWidget.clear()
        sorted_history = sorted(self._history.keys(), key=lambda x: self._history[x], reverse=True)
        for i in sorted_history:
            item = QtWidgets.QListWidgetItem(i)
            self.listWidget.addItem(item)

    def _onItemDoubleClicked(self, item):
        """双击列表项事件：选择标签，并判断是鼠标左键还是其它键"""
        mouse_buttons = QtWidgets.QApplication.mouseButtons()
        if mouse_buttons & QtCore.Qt.MouseButton.LeftButton:
            label_text = item.text()
            if label_text:
                self.lineEdit.setText(label_text)
        elif mouse_buttons & QtCore.Qt.MouseButton.RightButton:
            self.accept()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.reject()
        return super().closeEvent(event)

    def setPos(self, pos):
        x, y = utils.p2np_i(pos)
        self.label_range.setText(f"[{x},{y}]")

    def getPos(self) -> str:
        return json.loads(self.label_range.text())

    def get_data(self) -> str:
        d = {}
        d["pos"] = self.getPos()
        d["label"] = self.lineEdit.text()
        d["visibility"] = self.comboBox.currentIndex() == 0
        d["annotation_id"] = self.annotation_id
        return d

    def set_data(self, d: dict):
        self.setPos(d["pos"])
        self.lineEdit.setText(d["label"])
        self.comboBox.setCurrentIndex(0 if d["visibility"] else 1)
        self.annotation_id = d.get("annotation_id", -1)

    def showEvent(self, event) -> None:
        self.raise_()

    def accept(self):
        if self.lineEdit.text() == "":
            QtWidgets.QMessageBox.warning(self, self.tr("警告"), self.tr("请输入标注标签"))
            return
        self.accepted.emit()
        self.hide()

    def reject(self):
        self.rejected.emit()
        self.hide()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.hide()

    def closeEvent(self, event) -> None:
        self.reject()
        return super().closeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        match event.key():
            case QtCore.Qt.Key.Key_Escape:
                self.reject()
            case QtCore.Qt.Key.Key_F1:
                self.accept()
        return super().keyPressEvent(event)
