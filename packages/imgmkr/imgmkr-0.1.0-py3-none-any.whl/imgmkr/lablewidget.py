from PySide6 import QtCore, QtGui, QtWidgets
from .config import cfg
from .ui import label0_ui
from .shape import Shape

class Label0(QtWidgets.QWidget, label0_ui.Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("快速编辑"))
        self._history = cfg.getLabelHistory()
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.itemDoubleClicked.connect(self._onItemDoubleClicked)
        self.setListView()

    def addHistory(self, hs):
        self._history[hs]=1
        self.setListView()

    def setListView(self):
        self.listWidget.clear()
        sorted_history = sorted(self._history.keys(), key=lambda x: self._history[x], reverse=True)
        
        for label_text in sorted_history:
            # 创建自定义 widget
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 2, 5, 2)
            item_layout.setSpacing(5)
            
            # 标签文本
            label = QtWidgets.QLabel(label_text)
            label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
            item_layout.addWidget(label)
            
            # 追加按钮
            btn_append = QtWidgets.QToolButton()
            btn_append.setText(self.tr("追加"))
            btn_append.setToolTip(self.tr("追加此标签"))
            btn_append.clicked.connect(lambda checked=False, text=label_text: self._onAppendClicked(text))
            item_layout.addWidget(btn_append)
            
            # 创建列表项并设置自定义 widget
            list_item = QtWidgets.QListWidgetItem()
            # 将标签文本存储在列表项的数据中，以便双击时获取
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, label_text)
            # 设置合适的尺寸提示
            item_widget.setMinimumHeight(30)
            list_item.setSizeHint(QtCore.QSize(0, 30))
            self.listWidget.addItem(list_item)
            self.listWidget.setItemWidget(list_item, item_widget)
    
    def _onItemDoubleClicked(self, item):
        """双击列表项事件：选择标签，并判断是鼠标左键还是其它键"""
        mouse_buttons = QtWidgets.QApplication.mouseButtons()
        if mouse_buttons & QtCore.Qt.MouseButton.LeftButton:
            label_text = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if label_text:
                self._onSelectClicked(label_text)
        elif mouse_buttons & QtCore.Qt.MouseButton.RightButton:
            self.parent().accept()
    
    def _onSelectClicked(self, text):
        """选择按钮点击事件：替换当前文本"""
        self.lineEdit.setText(text)
        # self._history[text] = self._history.get(text, 0) + 1
        # cfg.setLabelHistory(self._history)
        # 更新列表以反映新的排序
        self.setListView()
    
    def _onAppendClicked(self, text):
        """追加按钮点击事件：追加到当前文本"""
        current_text = self.lineEdit.text()
        if current_text:
            self.lineEdit.setText(current_text + "," + text)
        else:
            self.lineEdit.setText(text)
        # self._history[text] = self._history.get(text, 0) + 1
        # cfg.setLabelHistory(self._history)
        # 更新列表以反映新的排序
        self.setListView()

    def showEvent(self, event):
        self.setListView()

class LableWidget(QtWidgets.QWidget):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()
    valueChanged = QtCore.Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("快速编辑"))
        self.current_table = None

        self.image_id = -1
        self.range = [0, 0, 0, 0]
        self.mark = ""

        # 创建布局
        layout = QtWidgets.QVBoxLayout(self)
        
        self.lb = Label0(self)
        layout.addWidget(self.lb)

        # 创建按钮
        button_layout = QtWidgets.QHBoxLayout()
        self.button_ok = QtWidgets.QPushButton(self.tr("确定"))
        self.button_cancel = QtWidgets.QPushButton(self.tr("取消"))
        button_layout.addStretch()
        button_layout.addWidget(self.button_ok)
        button_layout.addWidget(self.button_cancel)
        layout.addLayout(button_layout)
        
        # 连接信号
        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)
        
        # 设置对话框大小
        self.resize(300,600)

    def setRange(self, shape:Shape):
        self.range = shape.get_array_data()
        txt = f"[{','.join([str(i) for i in self.range])}]"
        self.lb.label_range.setToolTip(txt)
        if len(txt)>30:
            txt = txt[:30] + "..."
        self.lb.label_range.setText(txt)

    def getRange(self):
        return self.range

    def showEvent(self, event) -> None:
        self.raise_()

    def accept(self):
        if self.lb.lineEdit.text() == "":
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