from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from .ui.camera_ui import Ui_Form
import cv2
import numpy as np
import threading
import queue
import time


class CameraThread(threading.Thread):
    """相机视频流读取线程"""
    
    def __init__(self, camera_index, resolution=None, frame_queue=None):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.resolution = resolution
        self.frame_queue = frame_queue
        self.running = False
        self.cap = None
    
    def run(self):
        """线程主函数"""
        self.cap = cv2.VideoCapture(self.camera_index,cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            return
        
        # 如果指定了分辨率，设置相机分辨率
        if self.resolution:
            width, height = self.resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # 将帧放入队列（非阻塞，如果队列满了就丢弃旧帧）
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    # 队列满了，丢弃最旧的帧，放入新帧
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass
            else:
                break
            time.sleep(0.033)  # 约30fps
    
    def stop(self):
        """停止线程"""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.is_alive():
            self.join(timeout=1.0)

    def open_settings(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_SETTINGS,1)


class CameraWidget(QtWidgets.QWidget, Ui_Form):
    captured = QtCore.Signal(object)
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("camera preview widget")
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.imgItem = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.imgItem)
        self.comboBox_camera.currentIndexChanged.connect(self.on_camera_changed)
        self.pushButton_open.clicked.connect(self.open_camera)
        self.pushButton_settings.clicked.connect(self.open_settings)
        self.pushButton_capture.clicked.connect(self.capture)
        
        self.camera_thread = None
        self.current_frame = None
        self.selected_camera_index = 0  # OpenCV相机索引
        self.devices = []  # 保存设备列表以便查找索引
        self._last_view_size = None  # 记录上次的视图尺寸
        self.frame_queue = queue.Queue(maxsize=2)  # 帧队列，最多缓存2帧
        self.timer = QtCore.QTimer()  # 定时器用于检查队列
        self.timer.timeout.connect(self.check_frame_queue)

    def showEvent(self, event) -> None:
        self.enumerateCameras();
        return super().showEvent(event)

    def enumerateCameras(self):
        self.comboBox_camera.clear()
        self.devices = QtMultimedia.QMediaDevices.videoInputs()
        for idx, device in enumerate(self.devices):
            self.comboBox_camera.addItem(device.description(), idx)  # 存储索引而不是ID

    def on_camera_changed(self, index):
        if index < 0:
            return
        
        # 获取选中的相机索引
        camera_index = self.comboBox_camera.itemData(index)
        if camera_index is None or camera_index >= len(self.devices):
            return
        
        self.selected_camera_index = camera_index
        selected_device = self.devices[camera_index]
        
        # 清空分辨率列表
        self.comboBox_resolutions.clear()
        
        # 获取该设备支持的所有视频格式
        video_formats = selected_device.videoFormats()
        
        # 提取分辨率并去重
        resolutions = set()
        for format in video_formats:
            resolution = format.resolution()
            resolutions.add((resolution.width(), resolution.height()))
        
        # 按分辨率大小排序（从大到小）
        sorted_resolutions = sorted(resolutions, key=lambda x: (x[0] * x[1], x[0]), reverse=True)
        
        # 添加到下拉框
        for width, height in sorted_resolutions:
            resolution_text = f"{width}x{height}"
            self.comboBox_resolutions.addItem(resolution_text, (width, height))

    def open_camera(self):
        """使用OpenCV打开相机并在子线程中读取视频流"""
        # 如果已有线程在运行，先停止
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.stop()
            self.timer.stop()
            # 清空队列
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
        
        # 获取选中的分辨率（如果有）
        resolution = None
        if self.comboBox_resolutions.count() > 0:
            current_res_index = self.comboBox_resolutions.currentIndex()
            if current_res_index >= 0:
                resolution = self.comboBox_resolutions.itemData(current_res_index)
        
        # 创建并启动相机线程
        self.camera_thread = CameraThread(self.selected_camera_index, resolution, self.frame_queue)
        self.camera_thread.start()
        
        # 启动定时器检查队列（约30fps）
        self.timer.start(33)
    
    def check_frame_queue(self):
        """检查帧队列并处理帧"""
        try:
            frame = self.frame_queue.get_nowait()
            self.on_frame_received(frame)
        except queue.Empty:
            pass
    
    def on_frame_received(self, frame):
        """接收视频帧并显示"""
        # 将BGR转换为RGB
        self.current_frame = frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        
        # 转换为QImage
        q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        
        # 转换为QPixmap
        pixmap = QtGui.QPixmap.fromImage(q_image)
        
        # 获取graphicsView的尺寸（考虑滚动条）
        view_size = self.graphicsView.viewport().size()
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
            self.imgItem.setPixmap(scaled_pixmap)
            
            # 将imgItem居中：设置位置为(0, 0)，然后调整scene的rect
            self.imgItem.setPos(0, 0)
            # 更新scene的rect以匹配pixmap大小
            self.scene.setSceneRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
            
            # 居中显示（只在首次或尺寸变化时调用，避免频繁调用）
            if self._last_view_size is None or self._last_view_size.width() != view_size.width() or self._last_view_size.height() != view_size.height():
                self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
                self._last_view_size = QtCore.QSize(view_size)
        else:
            # 如果view还没有尺寸，直接设置原始pixmap
            self.imgItem.setPixmap(pixmap)
            self.imgItem.setPos(0, 0)
            self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
    
    def resizeEvent(self, event):
        """窗口大小改变时更新视图"""
        super().resizeEvent(event)
        # 重置视图尺寸，触发重新居中
        self._last_view_size = None
        if self.imgItem.pixmap() and not self.imgItem.pixmap().isNull():
            self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
    
    def closeEvent(self, event):
        """窗口关闭时停止相机线程"""
        self.timer.stop()
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.stop()
        super().closeEvent(event)

    def open_settings(self):
        if self.camera_thread and self.camera_thread.cap:
            self.camera_thread.open_settings()

    def capture(self):
        if self.current_frame is not None and self.camera_thread and self.camera_thread.cap:
            self.captured.emit(self.current_frame)
        