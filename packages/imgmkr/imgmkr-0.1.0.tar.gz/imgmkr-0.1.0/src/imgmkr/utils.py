from PySide6 import QtGui, QtCore
import numpy as np


def clip(x, min_value, max_value):
    return max(min(x, max_value), min_value)


def qpixmap2numpy(pixmap):
    """将 QPixmap 转换为 numpy 数组

    Args:
        pixmap: QPixmap 对象

    Returns:
        numpy.ndarray: 形状为 (height, width, 3) 的 BGR 数组
    """
    image = pixmap.toImage()
    image = image.convertToFormat(QtGui.QImage.Format.Format_BGR888)
    width = image.width()
    height = image.height()
    ptr = image.constBits()
    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 3))
    return arr.copy()


def p2np(p):
    if isinstance(p, QtCore.QPointF):
        pt = np.array([p.x(), p.y()])
    elif isinstance(p, QtCore.QPoint):
        pt = np.array([p.x(), p.y()])
    else:
        pt = np.array(p)
    return pt.astype("float")

def p2np_i(p):
    if isinstance(p, QtCore.QPointF):
        pt = np.array([p.x(), p.y()])
    elif isinstance(p, QtCore.QPoint):
        pt = np.array([p.x(), p.y()])
    else:
        pt = np.array(p)
    return pt.round().astype("int")


def is_point_near_segment(p, a, b, width):
    """
    判断点 p 是否在 线段 ab 的 'width' 范围内（即线宽为 width 的矩形带内）。

    参数:
        p: array-like, shape (2,) — 鼠标点击点 [px, py], 支持QPoint
        a: array-like, shape (2,) — 线段起点 [x1, y1], 支持QPoint
        b: array-like, shape (2,) — 线段终点 [x2, y2], 支持QPoint
        width: float — 线宽（直径），允许的总宽度

    返回:
        bool — True 表示在范围内
    """
    p = p2np(p)
    a = p2np(a)
    b = p2np(b)
    ab = b - a  # 向量 AB
    ap = p - a  # 向量 AP
    ab_len_sq = np.dot(ab, ab)  # |AB|²
    if ab_len_sq < 1e-12:  # A 和 B 几乎重合 → 退化为点
        dist_sq = np.dot(ap, ap)
        return dist_sq <= (width / 2) ** 2
    # 计算投影参数 t ∈ [0, 1]
    t = np.dot(ap, ab) / ab_len_sq
    t = np.clip(t, 0.0, 1.0)
    # 最近点 = a + t * ab
    closest = a + t * ab
    # 平方距离
    diff = p - closest
    dist_sq = np.dot(diff, diff)
    return dist_sq <= (width / 2) ** 2

def relation_polygon(p, polygon, width=5.0):
    """
    判断点 p 与多边形 polygon 的位置关系
    
    参数:
        p: array-like, shape (2,) — 待判断的点 [px, py], 支持 QPoint、QPointF 或 array-like
        polygon: list — 多边形的顶点列表，每个元素是 QPoint、QPointF 或 array-like
        width: float — 判断点是否在边上的线宽容忍度，默认 5.0
    
    返回:
        str — 'on' 表示在边上, 'in' 表示在内部, 'out' 表示在外部
    """
    if len(polygon) < 3:
        return 'out'
    
    p = p2np(p)
    
    # 第一步：检查点是否在多边形的任何一条边上
    n = len(polygon)
    for i in range(n):
        a = polygon[i]
        b = polygon[(i + 1) % n]  # 最后一条边连接最后一个点和第一个点
        if is_point_near_segment(p, a, b, width):
            return 'on'
    
    # 第二步：如果不在边上，使用射线法判断点是在内部还是外部
    # 从点向右发射一条水平射线，计算与多边形边的交点数
    px, py = p[0], p[1]
    intersections = 0
    
    for i in range(n):
        a = p2np(polygon[i])
        b = p2np(polygon[(i + 1) % n])
        
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        
        # 检查射线是否与线段相交
        # 射线是从 (px, py) 向右的水平线
        # 线段是从 (ax, ay) 到 (bx, by)
        
        # 排除水平线段（与射线平行）
        if abs(ay - by) < 1e-9:
            continue
        
        # 确保 ay < by（交换端点使 y 坐标递增）
        if ay > by:
            ax, ay, bx, by = bx, by, ax, ay
        
        # 检查射线的 y 坐标是否在线段的 y 范围内
        if py < ay or py >= by:
            continue
        
        # 计算射线与线段的交点的 x 坐标
        # 使用线性插值：x = ax + (py - ay) * (bx - ax) / (by - ay)
        if abs(by - ay) > 1e-9:
            x_intersect = ax + (py - ay) * (bx - ax) / (by - ay)
            # 如果交点在点的右侧，则计数
            if x_intersect > px:
                intersections += 1
    
    # 奇数个交点表示在内部，偶数个交点表示在外部
    return 'in' if intersections % 2 == 1 else 'out'
