from PySide6 import QtWidgets, QtGui, QtCore
from .ui.mainwindow_ui import Ui_MainWindow
import os
import sqlalchemy
from .utils import clip, qpixmap2numpy
from .model import Annotation, Image, Dataset
import functools
from .image_item import ImageItem
from . import lablewidget
from .config import cfg
import json
import time
from datetime import datetime
from . import res_rc
from . import camera
from .hover_preview_widget import HoverPreviewWidget
import cv2
import numpy as np
import importlib.util
import traceback
import subprocess
from .finder import Finder
import re
from .shape import Shape
from .labelwidget_keypoint import LabelWidgetKeypoint


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.lable_widget = lablewidget.LableWidget()
        self.lable_widget_keypoint = LabelWidgetKeypoint()
        self.setupUi(self)
        self.finder = Finder()
        self.setWindowTitle(self.tr("Image Annotation Tool"))
        self.camera_widget = camera.CameraWidget()

        if self.is_dark_theme():
            ico = QtGui.QIcon(":/vsicons/vscode-codicons/screen-full.svg")
            ico = self.tint_icon(ico, QtGui.Qt.GlobalColor.white)
            self.toolButton_fit_img.setIcon(ico)
            ico = QtGui.QIcon(":/vsicons/vscode-codicons/trash.svg")
            ico = self.tint_icon(ico, QtGui.Qt.GlobalColor.white)
            self.toolButton_rm.setIcon(ico)

        self.current_pixmap = None

        # * 初始化历史数据表格
        self.column_names = ["id", "label", "range", "keypoints", "image_id"]
        self.tableWidget_history.setColumnCount(len(self.column_names))
        self.tableWidget_history.setHorizontalHeaderLabels(self.column_names)
        self.tableWidget_history.setColumnWidth(0, 40)
        # self.tableWidget_history.verticalHeader().setVisible(False)
        # 允许编辑，但 id 和 image_id 列将设置为不可编辑
        self.tableWidget_history.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.tableWidget_history.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # 连接表格项修改信号
        self.tableWidget_history.itemChanged.connect(self.on_table_item_changed)

        self.pushButton_prev_img.clicked.connect(self.prevImage)
        self.pushButton_next_img.clicked.connect(self.nextImage)
        self.actionopen_dir.triggered.connect(functools.partial(self.setWorkDir))
        self.actionview_db_images.triggered.connect(self.setDbAsWorkDir)
        self.actionnext_new_image.triggered.connect(self.nextNewImage)
        self.actiongoto.triggered.connect(self.goto)
        self.actionremove_image.triggered.connect(self.removeImage)
        self.actionopen_camera.triggered.connect(self.show_camera_widget)
        self.camera_widget.captured.connect(self.on_camera_captured)
        self.pushButton_capture.clicked.connect(self.camera_widget.capture)
        # 为 pushButton_capture 安装事件过滤器以处理 hover 事件
        self.pushButton_capture.installEventFilter(self)
        self.actionfind_replace.triggered.connect(self.show_finder)
        # 连接finder信号
        self.finder.label_findit.connect(self.findit)
        self.finder.label_replaceit.connect(self.replaceit)
        self.finder.label_reset.connect(self.reset_replace)
        self.finder.finder_closed.connect(self.on_finder_closed)
        # 创建悬浮预览窗口
        self.hover_preview_widget = HoverPreviewWidget(self, self.camera_widget)

        self.label_workdir = QtWidgets.QLabel("Work Directory: ")
        self.statusbar.addWidget(self.label_workdir)
        self.label_current_image = QtWidgets.QLabel("Current Image: ")
        self.statusbar.addWidget(self.label_current_image)
        self.dataset = Dataset("dataset.db")
        self.current_workdir = ""
        self.image_list = []
        self.current_image_index = -1
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.image_item = ImageItem()
        self.scene.addItem(self.image_item)
        self.graphicsView.resizeEvent = self.resizeEvent
        # 确保QGraphicsView能正确传递鼠标事件
        self.graphicsView.setMouseTracking(True)
        QtWidgets.QApplication.instance().installEventFilter(self)
        # 右键拖拽平移相关变量
        self.right_button_pressed = False
        self.last_pan_point = QtCore.QPoint()
        self.cursor_overridden = False  # 标记是否已经设置了覆盖光标
        # 为graphicsView安装事件过滤器以处理右键拖拽
        self.graphicsView.viewport().installEventFilter(self)
        self.splitter.setSizes([750, 250])

        self.lable_widget.accepted.connect(self.addAnnotation)
        self.lable_widget.rejected.connect(self.cancleAddAnnotation)
        self.tableWidget_history.itemSelectionChanged.connect(self.setHighlightRectIdx)
        self.toolButton_rm.clicked.connect(self.deleteAnnotation)

        self.lable_widget_keypoint.accepted.connect(self.addKeypoint2Annotation)
        self.lable_widget_keypoint.rejected.connect(self.cancleAddKeypoint2Annotation)

        self.checkBox_showlabel.toggled.connect(self.image_item.setShowLabel)
        self.checkBox_show_all.toggled.connect(self.setNeedShowLabel)
        self.spinBox_zoom.valueChanged.connect(self.setZoom)
        self.spinBox_zoom.setValue(150)
        self.fit_screen = True
        self.current_zoom_factor = 1.0  # 保存当前的缩放因子

        self.toolButton_fit_img.clicked.connect(self.setFitScreen)
        self.pushButton_detect.clicked.connect(self.script_detect)
        self.toolButton_detector_script.clicked.connect(self.select_detector_script)
        self.lineEdit_detector.textChanged.connect(self.on_detector_changed)
        # image item signals
        self.image_item.signals.shape_drawed.connect(self.showLabelWidget)
        self.image_item.signals.current_shape.connect(self.lable_widget.setRange)
        self.image_item.signals.mouse_selected.connect(self.mouse_select_annotation)
        self.image_item.signals.mouse_change_label.connect(self.mouse_change_annotation)
        self.image_item.signals.mouse_change_range.connect(self.mouse_change_annotation_range)
        self.image_item.signals.keypoint_drawed.connect(self.showLabelWidgetKeypoint)
        self.image_item.signals.mouse_change_keypoint.connect(self.mouse_change_keypoint)

        self.buttonGroup_type.buttonClicked.connect(self.change_tool_type)

        self.detector = None

        self.actionadd_script.triggered.connect(self.add_script)
        self.script_actions = {}

        # finder相关变量：快照
        self.replace_snapshot = None  # 存储被替换的annotation的原始label，key为annotation_id，value为原始label

        #!初始化后的默认行为
        if cfg.getLastWorkDir():
            self.setWorkDir(cfg.getLastWorkDir())
            self.lineEdit_detector.setText(cfg.getDetectorScript())
        else:
            self.setDbAsWorkDir()
        # 初始化脚本列表
        self.update_script_list()
        if cfg.getDetectorScript():
            self.lineEdit_detector.setText(cfg.getDetectorScript())

    def is_dark_theme(self):
        palette = QtWidgets.QApplication.palette()
        # 获取窗口背景色
        bg_color = palette.color(QtGui.QPalette.ColorRole.Window)
        r, g, b = bg_color.red(), bg_color.green(), bg_color.blue()
        # 亮度简单判别
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128

    def tint_icon(self, icon, color):
        if icon.isNull():
            return QtGui.QIcon()
        sizes = icon.availableSizes()
        if sizes:
            size = max(sizes)
            pixmap = icon.pixmap(size)
        else:
            pixmap = icon.pixmap(24, 24)
            if pixmap.isNull():
                pixmap = QtGui.QPixmap(24, 24)
                pixmap.fill(QtGui.Qt.transparent)
        if pixmap.isNull():
            return QtGui.QIcon()
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QtGui.QIcon(pixmap)

    def setWorkDir(self, work_dir=""):
        if not os.path.exists(work_dir):
            work_dir = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Select Work Directory"), cfg.getLastWorkDir())
        if work_dir:
            cfg.setLastWorkDir(work_dir)
            self.current_workdir = work_dir
            self.label_workdir.setText("Work Directory: " + work_dir)
            self.image_list = []
            for root, dirs, files in os.walk(work_dir):
                for file in files:
                    if file.lower().endswith((".png", ".jpg", ".bmp")):
                        image_path = os.path.join(root, file)
                        self.image_list.append(image_path)
            if self.image_list:
                self.current_image_index = 0
                self.setImage()

    def setDbAsWorkDir(self):
        # 实现逻辑：设置数据库为图片列表来源，并刷新当前图片
        self.label_workdir.setText("Work Directory: Database")
        self.current_workdir = ""
        self.image_list = []
        images = self.dataset.session.scalars(sqlalchemy.select(Image)).all()
        for img_entry in images:
            # 将数据库图片对象放入image_list
            self.image_list.append(img_entry)
        if self.image_list:
            self.current_image_index = 0
            self.setImage()

    def setImage(self, select_annotation_id=None):
        self.current_image_index = clip(self.current_image_index, 0, len(self.image_list) - 1)
        image_path = self.image_list[self.current_image_index]
        if isinstance(image_path, Image):
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_path.data)
        else:
            pixmap = QtGui.QPixmap(image_path)
        self.current_pixmap = pixmap
        self.image_item.setPixmap(pixmap)
        self.image_item.setPos(0, 0)
        # 更新场景边界以确保正确显示
        self.scene.setSceneRect(self.image_item.boundingRect())
        if self.fit_screen:
            # 先重置变换，确保从干净状态开始
            self.graphicsView.resetTransform()
            self.graphicsView.fitInView(self.image_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            # 计算 fitInView 后的实际缩放比例并更新 spinBox_zoom
            transform = self.graphicsView.transform()
            zoom_factor = transform.m11()  # 获取 x 方向的缩放因子
            self.current_zoom_factor = zoom_factor
            zoom_percent = int(zoom_factor * 100)
            # 临时断开信号连接，避免触发 setZoom
            self.spinBox_zoom.valueChanged.disconnect(self.setZoom)
            self.spinBox_zoom.setValue(zoom_percent)
            self.spinBox_zoom.valueChanged.connect(self.setZoom)
        else:
            # 重置变换并应用当前缩放
            self.graphicsView.resetTransform()
            if self.current_zoom_factor != 1.0:
                self.graphicsView.scale(self.current_zoom_factor, self.current_zoom_factor)
        self.graphicsView.centerOn(self.image_item)
        # 显示图片路径信息
        if isinstance(image_path, Image):
            display_path = image_path.image_path if image_path.image_path else f"Database Image ID: {image_path.id}"
        else:
            display_path = image_path
        self.label_current_image.setText(self.tr(f"Current Image({self.current_image_index+1}/{len(self.image_list)}): {display_path}"))
        # self.setValue2Table("image_path", image_path)
        if isinstance(image_path, str):
            with open(image_path, "rb") as f:
                img = f.read()
            hash = Image.calHash(img)
            imgs = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash))
            if imgs is None:
                self.dataset.session.add(
                    Image(
                        image_path=image_path,
                        size=f"{pixmap.width()}x{pixmap.height()}",
                        data=img,
                        hash=hash,
                    )
                )
                self.dataset.session.commit()
            if imgs is None:
                # 上面已添加并commit，可以通过hash拿到
                img_entry = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash))
            else:
                img_entry = imgs
            image_id = img_entry.id
        else:
            image_id = image_path.id
        self.lable_widget.image_id = image_id
        self.updateAnnotationHistory()

        # 如果指定了select_annotation_id，选中对应的行
        if select_annotation_id is not None:
            for row in range(self.tableWidget_history.rowCount()):
                id_item = self.tableWidget_history.item(row, 0)
                if id_item and int(id_item.text()) == select_annotation_id:
                    self.tableWidget_history.setCurrentCell(row, 0)
                    self.tableWidget_history.selectRow(row)
                    break

    def resizeEvent(self, event):
        if self.fit_screen:
            # 先重置变换，确保从干净状态开始
            self.graphicsView.resetTransform()
            self.graphicsView.fitInView(self.image_item, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            # 计算 fitInView 后的实际缩放比例并更新 spinBox_zoom
            transform = self.graphicsView.transform()
            zoom_factor = transform.m11()  # 获取 x 方向的缩放因子
            self.current_zoom_factor = zoom_factor
            zoom_percent = int(zoom_factor * 100)
            # 临时断开信号连接，避免触发 setZoom
            self.spinBox_zoom.valueChanged.disconnect(self.setZoom)
            self.spinBox_zoom.setValue(zoom_percent)
            self.spinBox_zoom.valueChanged.connect(self.setZoom)
        else:
            # 重置变换并应用当前缩放
            self.graphicsView.resetTransform()
            if self.current_zoom_factor != 1.0:
                self.graphicsView.scale(self.current_zoom_factor, self.current_zoom_factor)
        self.graphicsView.centerOn(self.image_item)
        super().resizeEvent(event)

    def prevImage(self):
        if self.image_list:
            self.current_image_index -= 1
            self.setImage()
        else:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Work directory not set or no images in work directory"))

    def nextImage(self):
        if self.image_list:
            self.current_image_index += 1
            self.setImage()
        else:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Work directory not set or no images in work directory"))

    def nextNewImage(self):
        # 判断是工作目录模式还是数据库模式
        if self.current_workdir == "":
            # 数据库模式：批量查询所有没有注释的图片，直接跳转
            # 查询所有有注释的 image_id
            annotated_image_ids = set()
            annotated_results = self.dataset.session.scalars(sqlalchemy.select(Annotation.image_id).distinct()).all()
            annotated_image_ids.update(annotated_results)

            # 从当前位置开始查找下一个没有注释的图片
            start_index = self.current_image_index + 1
            found = False
            for i in range(start_index, len(self.image_list)):
                image_obj = self.image_list[i]
                if image_obj.id not in annotated_image_ids:
                    # 找到没有注释的图片，直接跳转
                    self.current_image_index = i
                    self.setImage()
                    found = True
                    break

            if not found:
                # 如果从当前位置往后没找到，从头开始查找
                for i in range(0, start_index):
                    image_obj = self.image_list[i]
                    if image_obj.id not in annotated_image_ids:
                        self.current_image_index = i
                        self.setImage()
                        found = True
                        break

                if not found:
                    QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("All images have been annotated"))
        else:
            # 工作目录模式：保持原有逻辑，每张图片都播放一次
            self.nextImage()
            if self.tableWidget_history.rowCount() > 0 and self.current_image_index < len(self.image_list) - 1:
                QtCore.QTimer.singleShot(20, self.nextNewImage)

    def goto(self):
        n, ok = QtWidgets.QInputDialog.getInt(self, self.tr("Go To"), self.tr("Please enter the image number to jump to:"), minValue=1, maxValue=len(self.image_list))
        if ok:
            # 序号n（1-based），在image_list中的索引是n-1
            if 1 <= n <= len(self.image_list):
                self.current_image_index = n - 1
                self.setImage()
            else:
                QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid image number"))

    def removeImage(self):
        """删除当前图片：先让用户确认，然后从本地和数据库中删除图片，如果这个图片有注释，就将相关的标注也全部删除"""
        if not self.image_list or self.current_image_index < 0:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("No image to delete"))
            return

        current_image = self.image_list[self.current_image_index]
        image_path_str = ""
        image_id = None

        if isinstance(current_image, str):
            image_path_str = current_image
            with open(image_path_str, "rb") as f:
                img_data = f.read()
            hash_val = Image.calHash(img_data)
            img_entry = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))
            if img_entry:
                image_id = img_entry.id
        else:
            image_id = current_image.id
            image_path_str = current_image.image_path if current_image.image_path else ""

        if image_id is None:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Cannot find image database record"))
            return

        annotations = self.dataset.session.query(Annotation).filter_by(image_id=image_id).all()
        annotation_count = len(annotations)

        if image_path_str:
            message = self.tr(f"Are you sure you want to delete this image?\n\nImage path: {image_path_str}")
        else:
            message = self.tr(f"Are you sure you want to delete the current image?")

        if annotation_count > 0:
            message += self.tr(f"\n\nThis image has {annotation_count} annotation(s), which will be deleted as well.")

        message += self.tr("\n\nThis operation cannot be undone!")

        reply = QtWidgets.QMessageBox.question(
            self, self.tr("Confirm Delete"), message, QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No
        )

        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        if annotation_count > 0:
            for ann in annotations:
                self.dataset.session.delete(ann)
            self.dataset.session.commit()
        img_entry = self.dataset.session.query(Image).filter_by(id=image_id).first()
        if img_entry:
            self.dataset.session.delete(img_entry)
            self.dataset.session.commit()

        if isinstance(current_image, str) and os.path.exists(current_image):
            try:
                os.remove(current_image)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr(f"Failed to delete local file: {str(e)}"))

        # 从 image_list 中移除该项
        self.image_list.pop(self.current_image_index)

        # 更新当前图片索引
        if len(self.image_list) == 0:
            # 如果没有图片了，清空显示
            self.current_image_index = -1
            self.image_item.setPixmap(QtGui.QPixmap())
            self.label_current_image.setText(self.tr("Current Image: None"))
            self.lable_widget.image_id = None
            # 清空标注历史表格
            self.tableWidget_history.setRowCount(0)
            self.image_item.shapes = []
            self.image_item.update()
        else:
            # 调整索引，确保不越界
            if self.current_image_index >= len(self.image_list):
                self.current_image_index = len(self.image_list) - 1
            # 显示下一张图片（或上一张，如果删除的是最后一张）
            self.setImage()

        QtWidgets.QMessageBox.information(self, self.tr("Success"), self.tr("Image deleted"))

    def updateAnnotationHistory(self, selected_id=None):
        self.tableWidget_history.setRowCount(0)
        image_id = self.lable_widget.image_id
        if image_id is None:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Image ID not found"))
            return
        results = self.dataset.session.query(Annotation).filter_by(image_id=image_id).all()
        self.tableWidget_history.setRowCount(len(results))
        self.image_item.shapes = []
        self.tableWidget_history.itemChanged.disconnect(self.on_table_item_changed)
        for i, r in enumerate(results):
            rect = json.loads(r.range)
            for j, attr in enumerate(self.column_names):
                item = QtWidgets.QTableWidgetItem(str(getattr(r, attr)))
                # id 和 image_id 列设置为不可编辑
                if attr in ["id", "image_id"]:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.tableWidget_history.setItem(i, j, item)
        if selected_id is not None:
            id_col_idx = self.column_names.index("id")
            for row in range(self.tableWidget_history.rowCount()):
                item = self.tableWidget_history.item(row, id_col_idx)
                if item and str(item.text()) == str(selected_id):
                    self.tableWidget_history.selectRow(row)
                    break
        self.tableWidget_history.itemChanged.connect(self.on_table_item_changed)
        self.setNeedShowLabel()

    def createShape(self, annotation_id: int | str, label: str, rngs: list, keypoints: list = []):
        if isinstance(annotation_id, str):
            annotation_id = int(annotation_id)
        if len(rngs) == 4:
            shape = Shape("rect", annotation_id)
            shape.set_array_data(rngs)
            shape.set_label(label)
            shape.keypoints = keypoints
            return shape
        elif len(rngs) % 2 == 0:
            shape = Shape("polygon", annotation_id)
            shape.set_array_data(rngs)
            shape.set_label(label)
            shape.keypoints = keypoints
            return shape

    def setNeedShowLabel(self):
        """更新image_item中显示的shapes"""
        if self.checkBox_show_all.isChecked():
            shapes = []
            row_count = self.tableWidget_history.rowCount()
            range_col_idx = self.column_names.index("range")
            label_col_idx = self.column_names.index("label")
            kt_idx = self.column_names.index("keypoints")
            id_col_idx = self.column_names.index("id")
            for row in range(row_count):
                item = self.tableWidget_history.item(row, range_col_idx)
                label = self.tableWidget_history.item(row, label_col_idx)
                kts_txt = self.tableWidget_history.item(row, kt_idx).text()
                kts = json.loads(kts_txt) if kts_txt else []
                annotation_id = self.tableWidget_history.item(row, id_col_idx)
                if item and label:
                    try:
                        shapes.append(self.createShape(annotation_id.text(), label.text(), json.loads(item.text()), kts))
                    except Exception:
                        pass
            self.image_item.shapes = shapes
            selected_rows = self.tableWidget_history.selectionModel().selectedRows()
            selected_row_idxs = [model_idx.row() for model_idx in selected_rows]
            for i in selected_row_idxs:
                self.image_item.shapes[i].set_highlight(True)
        else:
            shapes = []
            selected_rows = self.tableWidget_history.selectionModel().selectedRows()
            range_col_idx = self.column_names.index("range")
            label_col_idx = self.column_names.index("label")
            kt_idx = self.column_names.index("keypoints")
            id_col_idx = self.column_names.index("id")
            for model_idx in selected_rows:
                row = model_idx.row()
                item = self.tableWidget_history.item(row, range_col_idx)
                label = self.tableWidget_history.item(row, label_col_idx)
                kts_txt = self.tableWidget_history.item(row, kt_idx).text()
                kts = json.loads(kts_txt) if kts_txt else []
                annotation_id = self.tableWidget_history.item(row, id_col_idx)
                if item and label:
                    try:
                        shapes.append(self.createShape(annotation_id.text(), label.text(), json.loads(item.text()), kts))
                        shapes[-1].set_highlight(True)
                    except Exception:
                        pass
            self.image_item.shapes = shapes
        self.image_item.update()

    def addAnnotation(self):
        self.dataset.add_annotation(
            self.lable_widget.image_id,
            json.dumps(self.lable_widget.getRange()),
            self.lable_widget.lb.lineEdit.text(),
        )
        self.image_item.current_shape = None
        self.image_item.update()
        self.updateAnnotationHistory()

    def deleteAnnotation(self):
        selected_row = self.tableWidget_history.selectionModel().selectedRows()
        for i in selected_row:
            id_item = self.tableWidget_history.item(i.row(), 0)
            if id_item:
                record_id = id_item.text()
                record = self.dataset.session.query(Annotation).filter_by(id=record_id).first()
                if record:
                    self.dataset.session.delete(record)
                    self.dataset.session.commit()
        self.updateAnnotationHistory()

    def cancleAddAnnotation(self):
        self.image_item.current_shape = None
        self.image_item.update()

    def addKeypoint2Annotation(self):
        data = self.lable_widget_keypoint.get_data()
        annotation_id = data["annotation_id"]
        kt_idx = self.column_names.index("keypoints")
        for i in range(self.tableWidget_history.rowCount()):
            id_item = self.tableWidget_history.item(i, 0)
            if id_item:
                table_row_id = int(id_item.text())
                if table_row_id == annotation_id:
                    kts_item = self.tableWidget_history.item(i, kt_idx)
                    existing_keypoints_str = kts_item.text() if kts_item else ""
                    if existing_keypoints_str == "":
                        existing_keypoints = []
                    else:
                        try:
                            existing_keypoints = json.loads(existing_keypoints_str)
                        except json.JSONDecodeError:
                            existing_keypoints = []
                    if not isinstance(existing_keypoints, list):
                        existing_keypoints = []
                    new_keypoint = {k: v for k, v in data.items() if k not in ["annotation_id"]}
                    existing_keypoints.append(new_keypoint)
                    self.dataset.update_annotation(annotation_id, keypoints=json.dumps(existing_keypoints))
                    self.updateAnnotationHistory(table_row_id)
                    return

    def cancleAddKeypoint2Annotation(self):
        for i in self.image_item.shapes:
            i.remove_unlabeleed_keypoints()

    def showLabelWidget(self, pos):
        self.lable_widget.move(pos)
        # 如果 label_widget 会在桌面窗口外，就向上移动或向左移动
        desktop_rect = QtWidgets.QApplication.primaryScreen().availableGeometry()
        lable_widget_rect = self.lable_widget.frameGeometry()
        lable_widget_rect.moveTopLeft(pos)

        x, y = lable_widget_rect.x(), lable_widget_rect.y()
        w, h = lable_widget_rect.width(), lable_widget_rect.height()

        # 检查右边越界
        if x + w > desktop_rect.right():
            x = desktop_rect.right() - w
        # 检查下边越界
        if y + h > desktop_rect.bottom():
            y = desktop_rect.bottom() - h
        # 检查左边越界
        if x < desktop_rect.left():
            x = desktop_rect.left()
        # 检查上边越界
        if y < desktop_rect.top():
            y = desktop_rect.top()

        self.lable_widget.move(x, y)
        self.lable_widget.show()

    def showLabelWidgetKeypoint(
        self,
        pos,
        kpos,
        annotation_id,
    ):
        self.lable_widget_keypoint.annotation_id = annotation_id
        self.lable_widget_keypoint.setPos(kpos)
        pos = QtCore.QPoint(pos.x() + 10, pos.y())
        desktop_rect = QtWidgets.QApplication.primaryScreen().availableGeometry()
        lable_widget_rect = self.lable_widget_keypoint.frameGeometry()
        lable_widget_rect.moveTopLeft(pos)
        x, y = lable_widget_rect.x(), lable_widget_rect.y()
        w, h = lable_widget_rect.width(), lable_widget_rect.height()
        # 检查右边越界
        if x + w > desktop_rect.right():
            x = desktop_rect.right() - w
        # 检查下边越界
        if y + h > desktop_rect.bottom():
            y = desktop_rect.bottom() - h
        # 检查左边越界
        if x < desktop_rect.left():
            x = desktop_rect.left()
        # 检查上边越界
        if y < desktop_rect.top():
            y = desktop_rect.top()
        self.lable_widget_keypoint.move(x, y)
        self.lable_widget_keypoint.show()

    def setHighlightRectIdx(self):
        self.setNeedShowLabel()

    def eventFilter(self, obj, event):
        # 处理graphicsView的右键拖拽平移（需要同时按下Ctrl键）
        if obj == self.graphicsView.viewport():
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                if isinstance(event, QtGui.QMouseEvent):
                    if event.button() == QtCore.Qt.MouseButton.RightButton and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                        self.right_button_pressed = True
                        self.last_pan_point = event.pos()
                        # 使用 QApplication.setOverrideCursor 强制设置光标，防止被其他组件覆盖
                        if not self.cursor_overridden:
                            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                            self.cursor_overridden = True
                        return True  # 事件已处理
            elif event.type() == QtCore.QEvent.Type.MouseMove:
                if isinstance(event, QtGui.QMouseEvent):
                    # 如果正在平移状态，优先处理
                    if self.right_button_pressed:
                        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.buttons() == QtCore.Qt.MouseButton.RightButton:
                            # 确保光标保持为手形（如果还没有设置覆盖光标，则设置）
                            if not self.cursor_overridden:
                                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                                self.cursor_overridden = True
                            # 计算鼠标移动距离
                            delta = event.pos() - self.last_pan_point
                            # 移动滚动条
                            h_scrollbar = self.graphicsView.horizontalScrollBar()
                            v_scrollbar = self.graphicsView.verticalScrollBar()
                            h_scrollbar.setValue(h_scrollbar.value() - delta.x())
                            v_scrollbar.setValue(v_scrollbar.value() - delta.y())
                            self.last_pan_point = event.pos()
                            return True  # 事件已处理，阻止其他处理
                        else:
                            # 如果松开Ctrl键或右键，重置状态
                            self.right_button_pressed = False
                            if self.cursor_overridden:
                                QtWidgets.QApplication.restoreOverrideCursor()
                                self.cursor_overridden = False
            elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                if isinstance(event, QtGui.QMouseEvent):
                    if event.button() == QtCore.Qt.MouseButton.RightButton:
                        if self.right_button_pressed:
                            self.right_button_pressed = False
                            # 恢复默认鼠标光标
                            if self.cursor_overridden:
                                QtWidgets.QApplication.restoreOverrideCursor()
                                self.cursor_overridden = False
                        return True  # 事件已处理

        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if self.lable_widget.isVisible():
                if isinstance(event, QtGui.QMouseEvent):
                    global_pos = event.globalPosition().toPoint()
                    lable_widget_rect = self.lable_widget.geometry()
                    if not lable_widget_rect.contains(global_pos):
                        self.lable_widget.hide()
        # 处理 pushButton_capture 的 hover 事件
        if obj == self.pushButton_capture:
            if event.type() == QtCore.QEvent.Type.Enter:
                self.on_pushButton_capture_hover_enter()
                return True
            elif event.type() == QtCore.QEvent.Type.Leave:
                self.on_pushButton_capture_hover_leave()
                return True
        # 处理滚轮事件：按住 Control 键时改变 spinBox_zoom 的值
        elif event.type() == QtCore.QEvent.Type.Wheel:
            if isinstance(event, QtGui.QWheelEvent):
                # 检查是否按下了 Control 键
                if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                    # 获取滚轮方向，正数向上，负数向下
                    delta = event.angleDelta().y()
                    if delta > 0:
                        # 向上滚动，增加缩放值
                        current_value = self.spinBox_zoom.value()
                        new_value = min(current_value + 5, self.spinBox_zoom.maximum())
                        self.spinBox_zoom.setValue(new_value)
                    elif delta < 0:
                        # 向下滚动，减少缩放值
                        current_value = self.spinBox_zoom.value()
                        new_value = max(current_value - 5, self.spinBox_zoom.minimum())
                        self.spinBox_zoom.setValue(new_value)
                    return True  # 事件已处理，不再传播
        elif event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Delete:
                # 触发删除选中的annotation
                self.deleteAnnotation()
                return True  # 事件已处理，不再传播
            elif event.key() == QtCore.Qt.Key.Key_W and self.image_item.hasFocus():
                self.pushButton_prev_img.click()
                return True
            elif event.key() == QtCore.Qt.Key.Key_S and self.image_item.hasFocus():
                self.pushButton_next_img.click()
                return True
        return super().eventFilter(obj, event)

    def setZoom(self):
        self.fit_screen = False
        zoom = self.spinBox_zoom.value() / 100
        self.current_zoom_factor = zoom
        # 重置变换矩阵，然后应用新的缩放值
        self.graphicsView.resetTransform()
        if zoom != 1.0:
            self.graphicsView.scale(zoom, zoom)
        self.graphicsView.centerOn(self.image_item)
        self.image_item.update()

    def setFitScreen(self):
        self.fit_screen = True
        self.setImage()
        # 计算 fitInView 后的实际缩放比例并更新 spinBox_zoom
        transform = self.graphicsView.transform()
        zoom_factor = transform.m11()  # 获取 x 方向的缩放因子
        zoom_percent = int(zoom_factor * 100)
        # 临时断开信号连接，避免触发 setZoom
        self.spinBox_zoom.valueChanged.disconnect(self.setZoom)
        self.spinBox_zoom.setValue(zoom_percent)
        self.spinBox_zoom.valueChanged.connect(self.setZoom)
        self.current_zoom_factor = zoom_factor

    def on_table_item_changed(self, item):
        """当表格项被修改时，同步更新数据库"""
        if item is None:
            return

        row = item.row()
        col = item.column()
        column_name = self.column_names[col]

        # id 和 image_id 列不应该被修改，如果被修改则忽略
        if column_name in ["id", "image_id"]:
            return

        # 获取该行的 id（用于数据库更新）
        id_item = self.tableWidget_history.item(row, 0)
        if id_item is None:
            return

        try:
            annotation_id = int(id_item.text())
        except ValueError:
            return

        # 根据修改的列更新数据库
        if column_name == "label":
            new_label = item.text()
            self.dataset.update_annotation(annotation_id, label=new_label)
        elif column_name == "range":
            new_range = item.text()
            # 验证 range 是否为有效的 JSON
            try:
                json.loads(new_range)
                self.dataset.update_annotation(annotation_id, rng=new_range)
                # 更新显示
                self.setNeedShowLabel()
            except json.JSONDecodeError:
                # 如果 JSON 无效，恢复原值
                QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid range format, must be valid JSON"))
                # 重新加载该行的数据
                annotation = self.dataset.session.query(Annotation).filter_by(id=annotation_id).first()
                if annotation:
                    item.setText(annotation.range)
                return
        elif column_name == "keypoints":
            new_kps = item.text()
            # 验证 range 是否为有效的 JSON
            self.dataset.update_annotation(annotation_id, keypoints=new_kps)
            # 更新显示
            self.setNeedShowLabel()

    def mouse_select_annotation(self, shape):
        for row in range(self.tableWidget_history.rowCount()):
            annotation_id = int(self.tableWidget_history.item(row, 0).text())
            if annotation_id == shape.annotation_id:
                try:
                    self.tableWidget_history.setCurrentCell(row, 0)
                    self.tableWidget_history.selectRow(row)
                    return
                except:
                    pass
        self.tableWidget_history.clearSelection()

    def mouse_change_annotation(self, it):
        shape, new_label = it
        rng = shape.get_array_data()
        label = shape.get_label()
        # 遍历表格找到与传入的 range/label 都一致的行并更新
        for row in range(self.tableWidget_history.rowCount()):
            item_range = self.tableWidget_history.item(row, 2)
            item_label = self.tableWidget_history.item(row, 1)
            if item_range and item_label:
                try:
                    range_data = json.loads(item_range.text())
                    if range_data == rng:
                        if item_label.text() == label:
                            # 选中表格行
                            self.tableWidget_history.setCurrentCell(row, 0)
                            self.tableWidget_history.selectRow(row)
                            # 更新label
                            item_label.setText(new_label)
                            # 更新数据库和显示
                            id_item = self.tableWidget_history.item(row, 0)
                            if id_item:
                                try:
                                    annotation_id = int(id_item.text())
                                    self.dataset.update_annotation(annotation_id, label=new_label)
                                except ValueError:
                                    pass
                            self.updateAnnotationHistory()
                            return
                except:
                    pass

    def mouse_change_annotation_range(self, it: list[Shape]):
        """处理鼠标修改annotation范围的信号
        it: [原始数据, 新数据] - 都是数组格式的range数据
        """
        original_shape, new_shape = it
        # 遍历表格找到与传入的 range 一致的行
        for row in range(self.tableWidget_history.rowCount()):
            annotation_id = int(self.tableWidget_history.item(row, 0).text())
            if annotation_id == original_shape.annotation_id:
                item_range = self.tableWidget_history.item(row, 2)
                item_range.setText(json.dumps(new_shape.get_array_data()))
                item_keypoint = self.tableWidget_history.item(row, 3)
                item_keypoint.setText(json.dumps(new_shape.keypoints))
                self.dataset.update_annotation(annotation_id=annotation_id, rng=item_range.text(), keypoints=item_keypoint.text())
                break

    def mouse_change_keypoint(self, kts, annotation_id):
        # 从表格中找到指定 annotation_id 的行，更新 keypoints 字段
        for row in range(self.tableWidget_history.rowCount()):
            id_item = self.tableWidget_history.item(row, 0)
            if id_item:
                try:
                    table_row_id = int(id_item.text())
                    if table_row_id == annotation_id:
                        # 更新数据库
                        self.dataset.update_annotation(annotation_id, keypoints=json.dumps(kts))
                        # 更新表格显示
                        kt_idx = self.column_names.index("keypoints") if "keypoints" in self.column_names else None
                        if kt_idx is not None:
                            kts_str = json.dumps(kts)
                            kts_item = self.tableWidget_history.item(row, kt_idx)
                            if kts_item:
                                kts_item.setText(kts_str)
                            else:
                                self.tableWidget_history.setItem(row, kt_idx, QtWidgets.QTableWidgetItem(kts_str))
                        # 更新显示
                        self.setNeedShowLabel()
                        break
                except Exception:
                    pass

    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == QtCore.QEvent.Type.ActivationChange:
            # 当mainwindow激活时，如果finder可见，提升finder
            if self.isActiveWindow() and self.finder.isVisible():
                QtCore.QTimer.singleShot(0, lambda: self.finder.raise_())
        super().changeEvent(event)

    def closeEvent(self, event):
        if self.camera_widget.isVisible():
            self.camera_widget.close()
        cfg.setDetectorScript(self.lineEdit_detector.text())
        cfg.save_config()
        self.lable_widget.close()
        self.lable_widget_keypoint.close()
        super().closeEvent(event)

    def show_camera_widget(self):
        if self.camera_widget.isVisible():
            self.camera_widget.raise_()
        else:
            self.camera_widget.show()

    def on_camera_captured(self, frame):
        """处理相机捕获的图像
        如果设置了工作目录，保存到工作目录；否则保存到数据库
        保存后显示当前图像
        """
        # 获取图像尺寸
        height, width = frame.shape[:2]
        size_str = f"{width}x{height}"

        # 将numpy数组编码为JPEG格式的字节数据
        success, encoded_image = cv2.imencode(".jpg", frame)
        if not success:
            QtWidgets.QMessageBox.warning(self, self.tr("Error"), self.tr("Image encoding failed"))
            return

        image_data = encoded_image.tobytes()

        # 检查是否设置了工作目录
        work_dir = self.current_workdir

        if work_dir and os.path.exists(work_dir):
            # 如果设置了工作目录，保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 精确到毫秒
            filename = f"{timestamp}.jpg"
            file_path = os.path.join(work_dir, filename)

            # 将编码后的图像数据直接写入文件
            with open(file_path, "wb") as f:
                f.write(image_data)

            # 添加到image_list
            if not self.image_list:
                self.image_list = []
            self.image_list.append(file_path)
            self.current_image_index = len(self.image_list) - 1

            # 同时保存到数据库（用于标注功能）
            hash_val = Image.calHash(image_data)
            img_entry = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))
            if img_entry is None:
                self.dataset.session.add(
                    Image(
                        image_path=file_path,
                        size=size_str,
                        data=image_data,
                        hash=hash_val,
                    )
                )
                self.dataset.session.commit()
        else:
            # 如果没有设置工作目录，保存到数据库
            hash_val = Image.calHash(image_data)
            img_entry = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))

            if img_entry is None:
                # 创建新的Image对象
                img_entry = Image(
                    image_path=None,  # 数据库中的图片没有文件路径
                    size=size_str,
                    data=image_data,
                    hash=hash_val,
                )
                self.dataset.session.add(img_entry)
                self.dataset.session.commit()

            # 添加到image_list（使用Image对象）
            if not self.image_list:
                self.image_list = []
            self.image_list.append(img_entry)
            self.current_image_index = len(self.image_list) - 1

        # 显示当前图像
        self.setImage()

    def on_pushButton_capture_hover_enter(self):
        """当鼠标进入 pushButton_capture 按钮时触发"""
        self.hover_preview_widget.show_at_position(self.pushButton_capture)

    def on_pushButton_capture_hover_leave(self):
        """当鼠标离开 pushButton_capture 按钮时触发"""
        self.hover_preview_widget.hide_preview()

    def load_detector_script(self):
        try:
            spec = importlib.util.spec_from_file_location("detector", self.lineEdit_detector.text())
            if spec is None:
                raise ImportError(f"Cannot load file: {self.lineEdit_detector.text()}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.detector = module.detect
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, self.tr("Error"), self.tr(f"Failed to load detection script: {e}"))
            self.detector = None

    def script_detect(self):
        try:
            if self.detector is None:
                self.load_detector_script()
            if self.current_pixmap is not None:
                results = self.detector(qpixmap2numpy(self.current_pixmap))
                # 获取当前图片的 image_id
                image_id = self.lable_widget.image_id
                if image_id is None:
                    QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Current image ID not found"))
                    return
                for lb, rng, kps in results:
                    self.dataset.add_annotation(image_id, json.dumps(rng), lb, json.dumps(kps))
                self.updateAnnotationHistory()
        except:
            traceback.print_exc()

    def select_detector_script(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Select Detection Script File (py format)"), "", "python module (*.py)")
        if file_name:
            cfg.setDetectorScript(file_name)
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr(f"Selected model: {file_name}"))
            self.lineEdit_detector.setText(file_name)

    def on_detector_changed(self):
        self.detector = None

    def add_script(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Select Script File (py format)"), "", "python module (*.py)")
        if file_name:
            cfg.addScript(file_name)
            self.update_script_list()

    def update_script_list(self):
        scripts = cfg.getScripts()
        # 清除旧的脚本菜单项（保留 add_script 和分隔符）
        actions_to_remove = []
        for action in self.menuscripts.actions():
            if action not in [self.actionadd_script]:
                # 检查是否是分隔符
                if not action.isSeparator():
                    actions_to_remove.append(action)
        for action in actions_to_remove:
            self.menuscripts.removeAction(action)

        # 清除旧的 script_actions
        self.script_actions = {}

        # 为每个脚本创建子菜单
        for i in range(len(scripts)):
            script_path = scripts[i]
            script_name = os.path.basename(script_path) + f"({i})"

            # 创建子菜单
            script_menu = QtWidgets.QMenu(script_name, self.menuscripts)
            self.menuscripts.addMenu(script_menu)

            # 创建 run action
            run_action = QtGui.QAction(self.tr("Run"), self)
            run_action.triggered.connect(lambda checked, script=script_path: self.run_script(script))
            script_menu.addAction(run_action)

            # 创建 remove action
            remove_action = QtGui.QAction(self.tr("Remove"), self)
            remove_action.triggered.connect(lambda checked, script=script_path: self.remove_script(script))
            script_menu.addAction(remove_action)

            # 保存菜单和脚本路径的映射
            self.script_actions[script_menu] = script_path

    def run_script(self, script):
        print(f"run::", f"python {script}")
        subprocess.Popen(f"python {script}", shell=True)

    def remove_script(self, script):
        """从配置中删除脚本并更新菜单列表"""
        reply = QtWidgets.QMessageBox.question(
            self,
            self.tr("Confirm Delete"),
            self.tr(f"Are you sure you want to delete this script?\n\n{script}"),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            cfg.removeScript(script)
            cfg.save_config()
            self.update_script_list()

    def findit(self, txt: str, backward: bool, regx: bool):
        """查找label匹配的annotation
        txt: 查找文本
        backward: 是否向后查找
        regx: 是否使用正则表达式
        """
        if not txt:
            return

        # 获取所有annotation
        all_annotations = self.dataset.session.query(Annotation).all()

        # 构建匹配的annotation列表
        matched_annotations = []
        for ann in all_annotations:
            label = ann.label
            if label is None:
                continue

            matched = False
            if regx:
                try:
                    if re.fullmatch(txt, label):
                        matched = True
                except re.error:
                    # 正则表达式错误，忽略
                    pass
            else:
                if txt.lower() in label.lower():
                    matched = True

            if matched:
                matched_annotations.append(ann)

        if not matched_annotations:
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("No matching annotation found"))
            return

        # 确定当前查找位置
        current_ann_id = None
        if self.tableWidget_history.rowCount() > 0:
            selected_rows = self.tableWidget_history.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                id_item = self.tableWidget_history.item(row, 0)
                if id_item:
                    current_ann_id = int(id_item.text())

        # 找到当前annotation在匹配列表中的位置
        current_index = -1
        if current_ann_id is not None:
            for i, ann in enumerate(matched_annotations):
                if ann.id == current_ann_id:
                    current_index = i
                    break

        # 确定下一个要查找的annotation
        if backward:
            # 向后查找
            if current_index > 0:
                next_index = current_index - 1
            else:
                next_index = len(matched_annotations) - 1
        else:
            # 向前查找
            if current_index < len(matched_annotations) - 1:
                next_index = current_index + 1
            else:
                next_index = 0

        # 获取下一个annotation
        next_ann = matched_annotations[next_index]

        # 找到对应的image并显示
        image_id = next_ann.image_id
        # 在image_list中找到对应的image
        image_index = -1
        for i, img in enumerate(self.image_list):
            if isinstance(img, Image):
                if img.id == image_id:
                    image_index = i
                    break
            else:
                # 字符串路径，需要通过hash查找
                try:
                    with open(img, "rb") as f:
                        img_data = f.read()
                    hash_val = Image.calHash(img_data)
                    img_entry = self.dataset.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))
                    if img_entry and img_entry.id == image_id:
                        image_index = i
                        break
                except Exception:
                    # 文件不存在或其他错误，跳过
                    continue

        # 如果image_list中没有找到，尝试从数据库获取
        if image_index < 0:
            img_entry = self.dataset.session.query(Image).filter_by(id=image_id).first()
            if img_entry:
                # 如果是数据库模式，直接添加到image_list
                if self.current_workdir == "":
                    # 检查是否已经在image_list中
                    found = False
                    for i, img in enumerate(self.image_list):
                        if isinstance(img, Image) and img.id == image_id:
                            image_index = i
                            found = True
                            break
                    if not found:
                        # 添加到image_list
                        self.image_list.append(img_entry)
                        image_index = len(self.image_list) - 1
                else:
                    # 工作目录模式，但图片不在列表中，提示用户
                    QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Cannot find image in current work directory"))
                    return

        if image_index >= 0:
            self.current_image_index = image_index
            self.setImage(select_annotation_id=next_ann.id)
        else:
            QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Cannot find image for annotation"))

    def replaceit(self, find_txt: str, replace_txt: str, regx: bool, replace_all: bool):
        """替换label
        find_txt: 查找文本
        replace_txt: 替换文本
        regx: 是否使用正则表达式
        replace_all: 是否替换所有
        """
        if not find_txt:
            return

        # 初始化快照（如果还没有初始化）
        if self.replace_snapshot is None:
            self.replace_snapshot = {}

        # 获取所有annotation
        all_annotations = self.dataset.session.query(Annotation).all()

        # 查找匹配的annotation
        matched_annotations = []
        for ann in all_annotations:
            label = ann.label
            if label is None:
                continue

            matched = False
            if regx:
                try:
                    if re.fullmatch(find_txt, label):
                        matched = True
                except re.error:
                    # 正则表达式错误，忽略
                    pass
            else:
                if find_txt.lower() in label.lower():
                    matched = True

            if matched:
                matched_annotations.append(ann)

        if not matched_annotations:
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("No matching annotation found"))
            return

        # 确定要替换的annotation列表
        if replace_all:
            # 替换所有匹配的，先确认
            match_count = len(matched_annotations)
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Replace All",
                f"Are you sure you want to replace all {match_count} matching annotation(s)?\n\nFind: {find_txt}\nReplace: {replace_txt}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
            to_replace = matched_annotations
        else:
            # 只替换当前选中的
            current_ann_id = None
            if self.tableWidget_history.rowCount() > 0:
                selected_rows = self.tableWidget_history.selectionModel().selectedRows()
                if selected_rows:
                    row = selected_rows[0].row()
                    id_item = self.tableWidget_history.item(row, 0)
                    if id_item:
                        current_ann_id = int(id_item.text())

            # 找到当前annotation是否在匹配列表中
            to_replace = []
            if current_ann_id is not None:
                for ann in matched_annotations:
                    if ann.id == current_ann_id:
                        to_replace.append(ann)
                        break

            if not to_replace:
                QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("Please select a matching annotation first"))
                return

        # 执行替换
        replaced_count = 0
        for ann in to_replace:
            old_label = ann.label
            if old_label is None:
                continue

            # 在第一次replace时保存原始label到快照（如果还没有记录）
            if ann.id not in self.replace_snapshot:
                self.replace_snapshot[ann.id] = old_label

            # 执行替换
            if regx:
                try:
                    new_label = re.sub(find_txt, replace_txt, old_label)
                except re.error:
                    QtWidgets.QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid regular expression"))
                    return
            else:
                # 简单字符串替换，保持大小写
                new_label = old_label.replace(find_txt, replace_txt)

            # 更新数据库
            self.dataset.update_annotation(ann.id, label=new_label)
            replaced_count += 1

        # 更新当前显示
        if self.current_image_index >= 0:
            self.updateAnnotationHistory()

        # 显示结果
        if replace_all:
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr(f"Replaced {replaced_count} annotation(s)"))
        else:
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("Replaced 1 annotation"))

    def reset_replace(self):
        """重置所有替换操作，恢复快照"""
        if self.replace_snapshot is None:
            QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr("No snapshot to reset"))
            return

        # 恢复所有记录的annotation
        restored_count = 0
        for ann_id, original_label in self.replace_snapshot.items():
            ann = self.dataset.session.query(Annotation).filter_by(id=ann_id).first()
            if ann:
                ann.label = original_label
                restored_count += 1

        # 提交更改
        if restored_count > 0:
            self.dataset.session.commit()

        # 清空快照
        self.replace_snapshot = None

        # 更新当前显示
        if self.current_image_index >= 0:
            self.updateAnnotationHistory()

        QtWidgets.QMessageBox.information(self, self.tr("Info"), self.tr(f"Reset {restored_count} annotation(s)"))

    def show_finder(self):
        """显示finder窗口，并设置位置使其保持在mainwindow上方"""
        if not self.finder.isVisible():
            # 设置finder位置在mainwindow上方
            mainwindow_pos = self.pos()
            mainwindow_size = self.size()
            finder_size = self.finder.size()

            # 计算finder位置：mainwindow右上角附近
            x = mainwindow_pos.x() + mainwindow_size.width() - finder_size.width() - 20
            y = mainwindow_pos.y() + 20

            # 确保finder不超出屏幕
            screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
            if x + finder_size.width() > screen.right():
                x = screen.right() - finder_size.width() - 10
            if x < screen.left():
                x = screen.left() + 10
            if y < screen.top():
                y = screen.top() + 10

            self.finder.move(x, y)

        self.finder.show()
        self.finder.raise_()
        self.finder.activateWindow()

    def on_finder_closed(self):
        """finder关闭时清理快照"""
        self.replace_snapshot = None

    def change_tool_type(self):
        btn = self.buttonGroup_type.checkedButton()
        # 切换工具类型时，清理当前正在绘制的shape
        if self.image_item.current_shape is not None:
            self.image_item.current_shape = None
            self.image_item.update()
        self.image_item.pen_type = btn.text()
