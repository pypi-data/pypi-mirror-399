import traceback
from PySide6 import QtWidgets, QtGui, QtCore
from . import utils
from .shape import Shape, CursorStatus
import copy


class ImageItemSignals(QtCore.QObject):
    current_shape = QtCore.Signal(object)  # 当前shape的数据
    shape_drawed = QtCore.Signal(object)  # position for poping up the label widget
    keypoint_drawed = QtCore.Signal(object, object, int)  # pos,kpos and annotation id
    mouse_selected = QtCore.Signal(object)  # 选中的shape对象
    mouse_selected_keypoint = QtCore.Signal(object)  # 选中的keypoint对象
    mouse_change_keypoint = QtCore.Signal(object, int)  # kts,annotation_id
    mouse_change_label = QtCore.Signal(object)  # [shape, new_label]
    mouse_change_range = QtCore.Signal(object)  # [original_data, new_data]


class ImageItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        self.signals = ImageItemSignals()
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsPixmapItem.ItemIsFocusable, True)
        self.setFlag(QtWidgets.QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.pen_type = "bbox"  #!pylogon bbox keypoint
        self.shapes: [Shape] = []  # Shape对象列表
        self.current_shape = None  # 当前正在绘制或编辑的shape
        self.pressed = False
        self.editing_shape_original = None  # 保存编辑前的原始shape快照
        self.show_label = True
        self.cs = CursorStatus.Null

    def setShowLabel(self, show_label):
        self.show_label = show_label
        self.update()

    def paint(self, painter: QtGui.QPainter, option, widget):
        super().paint(painter, option, widget)
        painter.drawRect(self.boundingRect())
        ratio = self.pixmap().width() / self.getViewSize().width()
        font = painter.font()
        font.setPointSizeF(utils.clip(10 * ratio, 10, 60))
        painter.setFont(font)
        # 绘制非高亮的shapes
        for i in self.shapes:
            if not i.is_highlight():
                i.paint(painter, ratio, font, self.show_label)
        # 绘制高亮的shapes
        for i in self.shapes:
            if i.is_highlight():
                i.paint(painter, ratio, font, self.show_label)
        # 绘制当前正在绘制或编辑的shape
        if self.current_shape is not None:
            self.current_shape.paint(painter, ratio, font, self.show_label)

    def get_editing_shape(self):
        if self.current_shape is not None and self.current_shape.is_editing():
            return self.current_shape
        for i in self.shapes:
            if i.is_editing():
                return i
        return Shape("null")

    def get_highlight_shape(self):
        hs = []
        for i in self.shapes:
            if i.is_highlight():
                hs.append(i)
        return hs

    def is_keypoint(self, pos):
        for i in self.shapes:
            for k in i.keypoints:
                if CursorStatus.nearPos(pos, k["pos"], 12):
                    return i, k
        return None, None

    def mousePressEvent(self, event) -> None:
        # 只处理左键，右键用于平移视图
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            if event.button() == QtCore.Qt.MouseButton.RightButton and self.pen_type == "keypoint":
                hs = self.get_highlight_shape()
                shape, keypoint = self.is_keypoint(event.pos())
                if shape and keypoint:
                    reply = QtWidgets.QMessageBox.question(None, "确认删除", "是否删除该关键点？", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                    if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                        shape.keypoints.remove(keypoint)
                        self.signals.mouse_change_keypoint.emit(shape.keypoints,shape.annotation_id)
                        self.update()
                return
        clicked_shape = self.is_select_rect(event.pos())
        if clicked_shape and (self.current_shape is None or not self.current_shape.continues):
            if clicked_shape.is_highlight() or clicked_shape == self.current_shape:
                # 获取点击位置的光标状态
                _, self.cs = clicked_shape.is_you(event.pos())
                if clicked_shape != self.current_shape:
                    self.editing_shape_original = copy.deepcopy(clicked_shape)
                clicked_shape.set_editing(True)
                self.pressed = True
                self.set_cursor()
                if clicked_shape == self.current_shape:
                    self.signals.mouse_selected.emit(clicked_shape)
                return
            else:
                # 如果未选中，则选中它
                self.signals.mouse_selected.emit(clicked_shape)
                return

        hs = self.get_highlight_shape()
        if len(hs) == 1 and self.pen_type == "keypoint":
            hs[0].push_keypoint(event.pos())
            self.signals.keypoint_drawed.emit(self.pos2global(event.pos()), event.pos(), hs[0].annotation_id)
            return

        # 如果当前有正在绘制的shape且类型不匹配，先清理
        if self.current_shape is not None and not self.current_shape.continues:
            self.current_shape = None
        self.editing_shape_original = None
        self.pressed = True
        if self.pen_type == "bbox":
            self.current_shape = Shape("rect")
            self.current_shape.push_data(event.pos())
            self.current_shape.push_data(event.pos())
            self.current_shape.set_editing(True)  # 设置为编辑状态，显示为红色
            self.cs = CursorStatus.Null
        elif self.pen_type == "polygon":
            if self.current_shape is None:
                self.current_shape = Shape("polygon")
                self.current_shape.push_data(event.pos())
                self.current_shape.push_data(event.pos())
                self.current_shape.continues = True
            else:
                self.current_shape.push_data(event.pos())
            self.current_shape.set_editing(True)  # 设置为编辑状态，显示为红色
            self.cs = CursorStatus.Null

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        # 只处理左键拖动
        if event.buttons() != QtCore.Qt.MouseButton.LeftButton:
            return
        editing_shape = self.get_editing_shape()
        if self.pressed:
            if editing_shape.dtype == "rect":
                # 获取当前rect的xywh格式
                xywh = editing_shape._rect_to_xywh(editing_shape._data)
                if not xywh:
                    return
                x, y, w, h = xywh
                px = event.pos().x()
                py = event.pos().y()
                match self.cs:
                    case CursorStatus.Null | CursorStatus.RECT_CENTER:
                        # 拖动整个rect（新建时）
                        editing_shape.change_rect("p2", event.pos())
                    case CursorStatus.RECT_LEFTTOP:
                        # 左上角：改变 x, y, w, h
                        new_w = w - (px - x)
                        new_h = h - (py - y)
                        editing_shape.change_rect("x", px)
                        editing_shape.change_rect("y", py)
                        editing_shape.change_rect("w", new_w)
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.RECT_LEFTBOTTOM:
                        # 左下角：改变 x, w, h；y 保持不变
                        new_w = w - (px - x)
                        new_h = py - y
                        editing_shape.change_rect("x", px)
                        editing_shape.change_rect("w", new_w)
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.RECT_RIGHTTOP:
                        # 右上角：改变 y, w, h；x 保持不变
                        new_w = px - x
                        new_h = h - (py - y)
                        editing_shape.change_rect("y", py)
                        editing_shape.change_rect("w", new_w)
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.RECT_RIGHTBOTTOM:
                        # 右下角：只改变 w, h；x, y 保持不变
                        new_w = px - x
                        new_h = py - y
                        editing_shape.change_rect("w", new_w)
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.RECT_LEFT:
                        # 左边：改变 x, w；y, h 保持不变
                        new_w = w - (px - x)
                        editing_shape.change_rect("x", px)
                        editing_shape.change_rect("w", new_w)
                    case CursorStatus.RECT_RIGHT:
                        # 右边：只改变 w；x, y, h 保持不变
                        new_w = px - x
                        editing_shape.change_rect("w", new_w)
                    case CursorStatus.RECT_TOP:
                        # 上边：改变 y, h；x, w 保持不变
                        new_h = h - (py - y)
                        editing_shape.change_rect("y", py)
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.RECT_BOTTOM:
                        # 下边：只改变 h；x, y, w 保持不变
                        new_h = py - y
                        editing_shape.change_rect("h", new_h)
                    case CursorStatus.KEYPOINT:
                        editing_shape.change_keypoint(event.pos())
                if editing_shape == self.current_shape:
                    self.signals.current_shape.emit(editing_shape)
                self.update()
            elif editing_shape.dtype == "polygon":
                # polygon的移动处理
                if len(editing_shape._data) > 0:
                    p = utils.p2np(event.pos())
                    editing_shape._data[-1] = [p[0], p[1]]
                self.update()
        else:
            # 更新光标状态
            for shape in self.shapes:
                if shape.is_highlight():
                    is_on, cs = shape.is_you(event.pos())
                    if is_on:
                        self.cs = cs
                        self.set_cursor()
                        return
            self.cs = CursorStatus.Null
            self.set_cursor()
            self.update()

    def hoverMoveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        # 处理鼠标悬停时的移动事件（没有按下按钮时）
        if (self.current_shape is not None) and self.current_shape.continues:
            if len(self.current_shape._data) > 0:
                p = utils.p2np(event.pos())
                self.current_shape._data[-1] = [p[0], p[1]]
            self.update()
            return

        editing_shape = self.get_editing_shape()
        if editing_shape is not None and editing_shape.is_valid():
            _, self.cs = editing_shape.is_you(event.pos())
            self.set_cursor()
        else:
            # 如果没有正在编辑的shape，检查是否悬停在已选中的shape上
            for shape in self.shapes:
                if shape.is_highlight():
                    is_on, cs = shape.is_you(event.pos())
                    if is_on:
                        self.cs = cs
                        self.set_cursor()
                        return
            self.cs = CursorStatus.Null
            self.set_cursor()
        super().hoverMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        # 只处理左键释放
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        self.pressed = False

        # 如果正在编辑已选中的shape（有editing_shape_original说明是编辑已存在的shape）
        editing_shape = self.get_editing_shape()
        if self.editing_shape_original is not None:
            if editing_shape.dtype == "rect" and editing_shape.is_valid():
                self.signals.mouse_change_range.emit([self.editing_shape_original,editing_shape])
                editing_shape.set_editing(False)
                self.editing_shape_original = None
                self.current_shape = None
                self.cs = CursorStatus.Null
                self.set_cursor()
                self.update()
                return

        # 如果是新建shape（is_editing为True但没有editing_shape_original）
        if self.current_shape is not None:
            if self.current_shape.dtype == "rect":
                xywh = self.current_shape._rect_to_xywh(self.current_shape._data)
                if xywh:
                    x, y, w, h = xywh
                    if abs(w) > 1 and abs(h) > 1 and abs(w * h) > 10:
                        # 获取 rect 的 x+w 和 y（item 本地坐标）
                        item_pos = QtCore.QPointF(x + w + 15, y)
                        self.signals.shape_drawed.emit(self.pos2global(item_pos))
                    else:
                        self.current_shape = None
            elif self.current_shape.dtype == "polygon":
                # polygon的处理在close_polygon中
                pass
        else:
            self.current_shape = None

        self.cs = CursorStatus.Null
        self.set_cursor()
        self.update()

    # def mouseDoubleClickEvent(self, event) -> None:
    #     shape = self.is_select_rect(event.pos())
    #     if shape:
    #         old_label = shape.get_label()
    #         new_label, ok = QtWidgets.QInputDialog.getText(None, "修改标签", "新标签:", QtWidgets.QLineEdit.Normal, old_label)
    #         if ok and new_label and new_label != old_label:
    #             # self.signals.mouse_change_label.emit([shape, new_label])
    #             pass
    #     return super().mouseDoubleClickEvent(event)

    def set_cursor(self):
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        if view:
            match self.cs:
                case CursorStatus.RECT_LEFTTOP | CursorStatus.RECT_RIGHTBOTTOM:
                    view.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
                case CursorStatus.RECT_RIGHTTOP | CursorStatus.RECT_LEFTBOTTOM:
                    view.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
                case CursorStatus.RECT_LEFT | CursorStatus.RECT_RIGHT:
                    view.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
                case CursorStatus.RECT_TOP | CursorStatus.RECT_BOTTOM:
                    view.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
                # case CursorStatus.RECT_CENTER:
                #     view.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
                case CursorStatus.Null:
                    view.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
                case _:
                    view.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def getViewSize(self):
        # 获取GraphicsView的视口大小
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        if view:
            return view.viewport().size()
        else:
            return self.boundingRect()

    def is_select_rect(self, pos):
        if self.current_shape is not None:
            is_on, _ = self.current_shape.is_you(pos)
            if is_on:
                return self.current_shape
        for shape in self.shapes:
            is_on, _ = shape.is_you(pos)
            if is_on:
                return shape
        return None

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        match event.key():
            case QtCore.Qt.Key.Key_Z:
                self.undo_polygon()
            case QtCore.Qt.Key.Key_C:
                self.close_polygon()

        return super().keyPressEvent(event)

    def close_polygon(self):
        if self.current_shape is None or self.pen_type != "polygon":
            return

        if len(self.current_shape._data) > 3:
            # 移除最后一个临时点
            self.current_shape._data.pop(-1)
            # 获取polygon的边界框
            x_coords = [p[0] for p in self.current_shape._data]
            y_coords = [p[1] for p in self.current_shape._data]
            x = max(x_coords)
            y = min(y_coords)
            self.signals.current_shape.emit(self.current_shape)
            p = QtCore.QPointF(x, y)
            self.signals.shape_drawed.emit(self.pos2global(p.toPoint()))
            self.current_shape.continues = False
        self.update()

    def undo_polygon(self):
        editing_shape = self.get_editing_shape()
        if editing_shape.dtype == "polygon":
            if len(editing_shape._data) > 0:
                editing_shape._data.pop(-1)
                self.update()
                if len(editing_shape._data) == 0:
                    if editing_shape == self.current_shape:
                        self.current_shape = None
                    else:
                        editing_shape.set_editing(False)

    def pos2global(self, pos):
        scene_pos = self.mapToScene(pos)
        # 获取视图并转换为屏幕坐标
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        view_pos = view.mapFromScene(scene_pos)
        global_pos = view.mapToGlobal(view_pos)
        return global_pos
