from PySide6 import QtWidgets, QtGui, QtCore
import cv2


class HoverPreviewWidget(QtWidgets.QWidget):
    """悬浮预览窗口，用于在鼠标悬停时显示相机画面"""
    
    def __init__(self, parent=None, camera_widget=None):
        super().__init__(parent)
        self.camera_widget = camera_widget
        
        # 设置窗口属性
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | 
            QtCore.Qt.WindowType.WindowStaysOnTopHint | 
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # 设置窗口大小
        self.resize(320, 240)
        
        # 创建布局和 graphicsView
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.graphics_view.setObjectName("hover_graphics_view")
        layout.addWidget(self.graphics_view)
        
        # 创建场景和图片项
        self.scene = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.img_item = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.img_item)
        
        # 创建定时器用于更新画面
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        
        # 初始状态隐藏
        self.hide()
    
    def set_camera_widget(self, camera_widget):
        """设置相机窗口引用"""
        self.camera_widget = camera_widget
    
    def update_frame(self):
        """更新预览窗口的画面"""
        if not self.camera_widget or self.camera_widget.current_frame is None:
            return
        
        # 获取当前帧
        frame = self.camera_widget.current_frame
        if frame is None:
            return
        
        # 将BGR转换为RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        
        # 转换为QImage
        q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        
        # 转换为QPixmap
        pixmap = QtGui.QPixmap.fromImage(q_image)
        
        # 获取graphicsView的尺寸
        view_size = self.graphics_view.viewport().size()
        if view_size.width() > 0 and view_size.height() > 0:
            # 计算缩放比例，保持宽高比
            scale_x = view_size.width() / pixmap.width()
            scale_y = view_size.height() / pixmap.height()
            scale = min(scale_x, scale_y)
            
            # 缩放pixmap
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * scale),
                int(pixmap.height() * scale),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            
            # 设置pixmap
            self.img_item.setPixmap(scaled_pixmap)
            
            # 设置位置并更新场景
            self.img_item.setPos(0, 0)
            self.scene.setSceneRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
            
            # 居中显示
            self.graphics_view.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # 如果view还没有尺寸，直接设置原始pixmap
            self.img_item.setPixmap(pixmap)
            self.img_item.setPos(0, 0)
            self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
    
    def show_at_position(self, button_widget):
        """在指定按钮下方显示预览窗口"""
        # 检查相机窗口是否打开且相机是否在运行
        if not self.camera_widget or not self.camera_widget.isVisible() or \
           not self.camera_widget.camera_thread or not self.camera_widget.camera_thread.is_alive():
            return
        
        # 获取按钮的全局位置
        button_global_pos = button_widget.mapToGlobal(QtCore.QPoint(0, 0))
        button_size = button_widget.size()
        
        # 计算悬浮窗口位置（按钮下方）
        preview_width = self.width()
        preview_height = self.height()
        
        # 获取屏幕可用区域
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        
        # 计算位置：按钮下方，居中对齐
        x = button_global_pos.x() + (button_size.width() - preview_width) // 2
        y = button_global_pos.y() + button_size.height() + 5  # 按钮下方5像素
        
        # 检查是否超出屏幕右边界
        if x + preview_width > screen.right():
            x = screen.right() - preview_width
        
        # 检查是否超出屏幕左边界
        if x < screen.left():
            x = screen.left()
        
        # 检查是否超出屏幕下边界（如果超出，显示在按钮上方）
        if y + preview_height > screen.bottom():
            y = button_global_pos.y() - preview_height - 5  # 按钮上方5像素
        
        # 设置窗口位置
        self.move(x, y)
        
        # 显示窗口并启动定时器
        self.show()
        self.update_timer.start(33)  # 约30fps
    
    def hide_preview(self):
        """隐藏预览窗口"""
        self.update_timer.stop()
        self.hide()

