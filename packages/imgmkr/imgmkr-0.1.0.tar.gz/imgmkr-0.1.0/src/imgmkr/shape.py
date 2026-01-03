from . import utils
from PySide6 import QtCore, QtGui
import numpy as np
from enum import Enum


class CursorStatus(Enum):
    Null = 0
    RECT_LEFTTOP = 1
    RECT_LEFTBOTTOM = 2
    RECT_RIGHTTOP = 3
    RECT_RIGHTBOTTOM = 4
    RECT_LEFT = 5
    RECT_RIGHT = 6
    RECT_TOP = 7
    RECT_BOTTOM = 8
    RECT_CENTER = 9
    POLYGON_LINE = 10
    POLYGON_POINT = 11
    KEYPOINT = 12

    @staticmethod
    def nearPos(p1, p2, r):
        p1 = utils.p2np(p1)
        p2 = utils.p2np(p2)
        x1, y1 = p1
        x2, y2 = p2
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= r**2

    @staticmethod
    def getStatus(pos, rect):
        if len(rect) == 4:
            x, y, w, h = rect
            px = pos.x()
            py = pos.y()

            b = 4
            if px < x - b or px > x + w + b or py < y - b or py > y + h + b:
                return CursorStatus.Null
            elif x + b < px < x + w - b and y + b < py < y + h - b:
                return CursorStatus.RECT_CENTER
            elif CursorStatus.nearPos(pos, QtCore.QPointF(x, y), b):
                return CursorStatus.RECT_LEFTTOP
            elif CursorStatus.nearPos(pos, QtCore.QPointF(x, y + h), b):
                return CursorStatus.RECT_LEFTBOTTOM
            elif CursorStatus.nearPos(pos, QtCore.QPointF(x + w, y), b):
                return CursorStatus.RECT_RIGHTTOP
            elif CursorStatus.nearPos(pos, QtCore.QPointF(x + w, y + h), b):
                return CursorStatus.RECT_RIGHTBOTTOM
            elif CursorStatus.nearPos(pos, QtCore.QPointF(x, y + h / 2), b):
                return CursorStatus.RECT_LEFT
            elif x - b < px < x + b:
                return CursorStatus.RECT_LEFT
            elif x + w - b < px < x + w + b:
                return CursorStatus.RECT_RIGHT
            elif y - b < py < y + b:
                return CursorStatus.RECT_TOP
            elif y + h - b < py < y + h + b:
                return CursorStatus.RECT_BOTTOM
        elif len(rect) > 4:
            match utils.relation_polygon(pos, [[rect[i], rect[i + 1]] for i in range(0, len(rect), 2)]):
                case "in":
                    return CursorStatus.RECT_CENTER
                case "out":
                    return CursorStatus.Null
                case "on":
                    return CursorStatus.POLYGON_LINE
        return CursorStatus.Null


class Shape:
    def __init__(self, dtype="rect", annotation_id=-1) -> None:
        self.dtype = dtype
        self._data = []  # rect:[[x1,y1],[x2,y2]]两点式,polygon:[[x,y],[x,y]...]
        self.keypoints = []  # {"label":"key","pos":[0,0],"visibility":True}
        self._label = ""
        self._hightlight = False
        self.__editing = False
        self.continues = False
        self.annotation_id = annotation_id
        self.editing_keypoint_idx = -1

    def _rect_to_xywh(self, data):
        """将两点式[[x1,y1],[x2,y2]]转换为xywh格式[x,y,w,h]"""
        if len(data) != 2 or len(data[0]) != 2 or len(data[1]) != 2:
            return None
        x1, y1 = data[0]
        x2, y2 = data[1]
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        return [x, y, w, h]

    def _xywh_to_rect(self, data):
        """将xywh格式[x,y,w,h]转换为两点式[[x1,y1],[x2,y2]]"""
        if len(data) != 4:
            return None
        x, y, w, h = data
        return [[x, y], [x + w, y + h]]

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def set_highlight(self, is_hightlight: bool):
        self._hightlight = is_hightlight

    def is_highlight(self) -> bool:
        return self._hightlight

    def change_rect(self, way, value):
        assert self.dtype == "rect", f"Key change_rect only supports rect dtype, but got dtype={self.dtype}"
        match way:
            case "x":
                # 修改x坐标，保持宽度不变
                x, y, w, h = self._rect_to_xywh(self._data)
                self._data = self._xywh_to_rect([value, y, w, h])
            case "y":
                # 修改y坐标，保持高度不变
                x, y, w, h = self._rect_to_xywh(self._data)
                self._data = self._xywh_to_rect([x, value, w, h])
            case "w":
                # 修改宽度，保持x坐标不变
                x, y, w, h = self._rect_to_xywh(self._data)
                self._data = self._xywh_to_rect([x, y, value, h])
            case "h":
                # 修改高度，保持y坐标不变
                x, y, w, h = self._rect_to_xywh(self._data)
                self._data = self._xywh_to_rect([x, y, w, value])
            case "p1":
                # 修改第一个点
                p = utils.p2np(value)
                self._data[0] = [p[0], p[1]]
            case "p2":
                # 修改第二个点
                p = utils.p2np(value)
                self._data[1] = [p[0], p[1]]
            case _:
                raise ValueError(f"Invalid way: {way}")

    def change_polygon(self, idx, value):
        assert self.dtype == "polygon", f"change_polygon only supports polygon dtype, but got dtype={self.dtype}"
        p = utils.p2np(value)
        self._data[idx] = [p[0], p[1]]

    def push_data(self, value):
        match self.dtype:
            case "rect":
                if len(self._data) == 0:
                    p = utils.p2np(value)
                    self._data = [[p[0], p[1]], [p[0], p[1]]]
                else:
                    self.change_rect("p2", value)
            case "polygon":
                p = utils.p2np(value)
                self._data.append([p[0], p[1]])
            case _:
                raise ValueError(f"Invalid dtype: {self.dtype}")

    def get_array_data(self):
        match self.dtype:
            case "rect":
                # 将两点式转换为xywh格式
                xywh = self._rect_to_xywh(self._data)
                return [int(round(i)) for i in xywh] if xywh else []
            case "polygon":
                return [int(round(i)) for p in self._data for i in p]
            case _:
                return []

    def set_array_data(self, data, dtype=None):
        if dtype is not None:
            self.dtype = dtype
        match self.dtype:
            case "rect":
                if len(data) == 4:
                    # 假设输入是xywh格式，转换为两点式存储
                    self._data = self._xywh_to_rect([float(data[0]), float(data[1]), float(data[2]), float(data[3])])
                else:
                    raise ValueError(f"Invalid data: {data}")
            case "polygon":
                if len(data) % 2 == 0:
                    self._data = [[float(i) for i in data[j : j + 2]] for j in range(0, len(data), 2)]
                else:
                    raise ValueError(f"Invalid data: {data}")
            case _:
                raise ValueError(f"Invalid dtype: {dtype}")

    def push_keypoint(self, p, visibility: bool = True):
        self.keypoints.append({"pos": utils.p2np(p), "label": "", "visibility": visibility})

    def remove_unlabeleed_keypoints(self):
        self.keypoints = [i for i in self.keypoints if i["label"] != ""]

    def set_editing(self, is_editing):
        self.__editing = is_editing

    def is_editing(self) -> bool:
        return self.__editing

    def clear(self):
        self._data = []
        self.keypoints = []

    def change_keypoint(self, pos,idx=None):
        if idx is None:
            idx = self.editing_keypoint_idx
        p = utils.p2np(pos).tolist()
        self.keypoints[idx]["pos"] = p

    def is_valid(self):
        match self.dtype:
            case "rect":
                return len(self._data) == 2 and len(self._data[0]) == 2 and len(self._data[1]) == 2
            case "polygon":
                return len(self._data) > 0
            case _:
                return False

    def is_unknown(self) -> bool:
        return self.dtype in ["rect", "polygon"]

    def paint(self, painter, ratio, font, show_label: bool):
        if not self.is_valid():
            return

        if self.is_editing():
            pen_color = QtCore.Qt.GlobalColor.red
            text_color = QtCore.Qt.GlobalColor.white
            keypoint_color = QtCore.Qt.GlobalColor.green
            pen_width = 2 * ratio
        elif self.is_highlight():
            keypoint_color = QtCore.Qt.GlobalColor.yellow
            pen_color = QtCore.Qt.GlobalColor.yellow
            text_color = QtCore.Qt.GlobalColor.red
            pen_width = 2 * ratio
        else:
            keypoint_color = QtCore.Qt.GlobalColor.green
            pen_color = QtCore.Qt.GlobalColor.green
            text_color = QtCore.Qt.GlobalColor.red
            pen_width = 1 * ratio

        painter.setPen(QtGui.QPen(pen_color, pen_width))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.transparent, QtCore.Qt.BrushStyle.SolidPattern))

        match self.dtype:
            case "rect":
                # 将两点式转换为xywh格式用于绘制
                xywh = self._rect_to_xywh(self._data)
                if xywh:
                    painter.drawRect(*xywh)
            case "polygon":
                polygon = [QtCore.QPointF(self._data[i][0], self._data[i][1]) for i in range(len(self._data))]
                painter.drawPolygon(polygon)
                point_color = QtCore.Qt.GlobalColor.red
                radius = 4 * ratio
                for pt in polygon:
                    if isinstance(pt, QtCore.QPointF):
                        x, y = pt.x(), pt.y()
                    else:
                        x, y = pt[0], pt[1]
                    painter.setPen(QtCore.Qt.GlobalColor.transparent)
                    painter.setBrush(QtGui.QBrush(point_color, QtCore.Qt.BrushStyle.SolidPattern))
                    painter.drawEllipse(QtCore.QPointF(x, y), radius, radius)
            case _:
                return

        for i in self.keypoints:
            x, y = i["pos"]
            keypoint_outer_color = keypoint_color
            keypoint_inner_color = QtCore.Qt.GlobalColor.red
            radius_small = 4 * ratio
            radius_big = 8 * ratio
            painter.setPen(QtCore.Qt.GlobalColor.transparent)
            painter.setBrush(QtGui.QBrush(keypoint_outer_color, QtCore.Qt.BrushStyle.SolidPattern))
            painter.drawEllipse(QtCore.QPointF(x, y), radius_big, radius_big)
            painter.setBrush(QtGui.QBrush(keypoint_inner_color, QtCore.Qt.BrushStyle.SolidPattern))
            painter.drawEllipse(QtCore.QPointF(x, y), radius_small, radius_small)
            # 设置文本颜色为可见的颜色
            if show_label:
                painter.setPen(QtGui.QPen(text_color, 1 * ratio))
                painter.drawText(QtCore.QPointF(x + radius_big, y), i["label"])

        if show_label and self._label:
            metrics = QtGui.QFontMetrics(painter.font())
            text_width = metrics.horizontalAdvance(self._label) + 8 * ratio  # 增加padding
            text_height = metrics.height() + 4 * ratio  # 增加padding

            # 根据shape类型计算label位置
            match self.dtype:
                case "rect":
                    xywh = self._rect_to_xywh(self._data)
                    if xywh:
                        x, y, w, h = xywh
                        text_x = x
                        text_y = y - text_height  # 在框的上方
                        top_y = y
                    else:
                        return
                    connect_point = None
                    text_alignment = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
                case "polygon":
                    # label的左下角连接到第一个点
                    if len(self._data) > 0:
                        first_point_x = self._data[0][0]
                        first_point_y = self._data[0][1]
                        text_x = first_point_x
                        text_y = first_point_y - text_height  # 文本底部在第一个点的y坐标
                        top_y = first_point_y
                        connect_point = QtCore.QPointF(first_point_x, first_point_y)
                        text_alignment = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom
                    else:
                        return
                case _:
                    return

            # 确保文本不超出画布顶部
            if text_y < 0:
                text_y = top_y

            text_rect = QtCore.QRectF(text_x, text_y, text_width, text_height)
            painter.save()
            painter.setPen(QtCore.Qt.GlobalColor.transparent)
            painter.setBrush(QtGui.QBrush(pen_color, QtCore.Qt.BrushStyle.SolidPattern))
            painter.setOpacity(0.9)
            painter.drawRect(text_rect)
            painter.restore()
            painter.save()
            painter.setPen(QtGui.QPen(pen_color, pen_width))
            if connect_point is not None:
                # polygon: 从第一个点连接到文本框底部
                painter.drawLine(connect_point, QtCore.QPointF(text_x, text_rect.bottom()))
            elif text_rect.bottom() >= top_y >= text_rect.top():
                pass
            else:
                # rect: 从顶部边缘画线
                painter.drawLine(QtCore.QPointF(text_x, top_y), QtCore.QPointF(text_x + text_width, top_y))
            painter.restore()
            painter.setPen(QtGui.QPen(text_color))
            painter.drawText(text_rect, text_alignment, self._label)

    def is_you(self, pos):
        """
        判断点是否在shape上（rect或多边形的边上）

        参数:
            pos: QPointF或QPoint - 要判断的点

        返回:
            tuple: (bool, CursorStatus) - 是否在shape上，以及光标状态
        """
        if not self.is_valid():
            return False, CursorStatus.Null

        self.editing_keypoint_idx = -1
        for idx, i in enumerate(self.keypoints):
            x, y = i["pos"]
            if CursorStatus.nearPos([x, y], pos, 16):
                self.editing_keypoint_idx = idx
                return True, CursorStatus.KEYPOINT

        match self.dtype:
            case "rect":
                xywh = self._rect_to_xywh(self._data)
                if not xywh:
                    return False, CursorStatus.Null
                x, y, w, h = xywh
                px = pos.x()
                py = pos.y()

                b = 8
                # 检查是否在rect外部
                if px < x - b or px > x + w + b or py < y - b or py > y + h + b:
                    return False, CursorStatus.Null

                # 检查是否在rect内部（不在边上）
                if x + b < px < x + w - b and y + b < py < y + h - b:
                    return False, CursorStatus.RECT_CENTER

                # 检查是否在角上
                if CursorStatus.nearPos(pos, QtCore.QPointF(x, y), b):
                    return True, CursorStatus.RECT_LEFTTOP
                elif CursorStatus.nearPos(pos, QtCore.QPointF(x, y + h), b):
                    return True, CursorStatus.RECT_LEFTBOTTOM
                elif CursorStatus.nearPos(pos, QtCore.QPointF(x + w, y), b):
                    return True, CursorStatus.RECT_RIGHTTOP
                elif CursorStatus.nearPos(pos, QtCore.QPointF(x + w, y + h), b):
                    return True, CursorStatus.RECT_RIGHTBOTTOM

                # 检查是否在边上
                if x - b < px < x + b:
                    return True, CursorStatus.RECT_LEFT
                elif x + w - b < px < x + w + b:
                    return True, CursorStatus.RECT_RIGHT
                elif y - b < py < y + b:
                    return True, CursorStatus.RECT_TOP
                elif y + h - b < py < y + h + b:
                    return True, CursorStatus.RECT_BOTTOM

                return False, CursorStatus.Null

            case "polygon":
                if len(self._data) < 3:
                    return False, CursorStatus.Null

                # 将polygon转换为点列表
                polygon_points = [[p[0], p[1]] for p in self._data]

                # 首先检查是否点击在polygon的点上
                b = 4
                for i, pt in enumerate(self._data):
                    if CursorStatus.nearPos(pos, QtCore.QPointF(pt[0], pt[1]), b):
                        return True, CursorStatus.POLYGON_POINT

                # 检查是否在多边形的边上
                relation = utils.relation_polygon(pos, polygon_points, width=5.0)
                if relation == "on":
                    return True, CursorStatus.POLYGON_LINE
                elif relation == "in":
                    return True, CursorStatus.RECT_CENTER  # 在内部也返回True
                else:
                    return False, CursorStatus.Null

            case _:
                return False, CursorStatus.Null

    def __str__(self):
        return f"{self.dtype} {self.__editing} {self._data}"
