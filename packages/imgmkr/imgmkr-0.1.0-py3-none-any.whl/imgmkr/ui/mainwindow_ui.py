# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGraphicsView, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QStatusBar, QTableWidget,
    QTableWidgetItem, QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1297, 935)
        self.actionopen = QAction(MainWindow)
        self.actionopen.setObjectName(u"actionopen")
        self.actionopen_dir = QAction(MainWindow)
        self.actionopen_dir.setObjectName(u"actionopen_dir")
        self.actionexport = QAction(MainWindow)
        self.actionexport.setObjectName(u"actionexport")
        self.actionview_db_images = QAction(MainWindow)
        self.actionview_db_images.setObjectName(u"actionview_db_images")
        self.actionnext_new_image = QAction(MainWindow)
        self.actionnext_new_image.setObjectName(u"actionnext_new_image")
        self.actionend_image = QAction(MainWindow)
        self.actionend_image.setObjectName(u"actionend_image")
        self.actionopen_camera = QAction(MainWindow)
        self.actionopen_camera.setObjectName(u"actionopen_camera")
        self.actionclose_camera = QAction(MainWindow)
        self.actionclose_camera.setObjectName(u"actionclose_camera")
        self.actiongoto = QAction(MainWindow)
        self.actiongoto.setObjectName(u"actiongoto")
        self.actionremove_image = QAction(MainWindow)
        self.actionremove_image.setObjectName(u"actionremove_image")
        self.actionset_train_script = QAction(MainWindow)
        self.actionset_train_script.setObjectName(u"actionset_train_script")
        self.actionstart_train = QAction(MainWindow)
        self.actionstart_train.setObjectName(u"actionstart_train")
        self.actionadd_script = QAction(MainWindow)
        self.actionadd_script.setObjectName(u"actionadd_script")
        self.actionfind_replace = QAction(MainWindow)
        self.actionfind_replace.setObjectName(u"actionfind_replace")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(16777215, 28))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.spinBox_zoom = QSpinBox(self.widget)
        self.spinBox_zoom.setObjectName(u"spinBox_zoom")
        self.spinBox_zoom.setMinimum(1)
        self.spinBox_zoom.setMaximum(400)

        self.horizontalLayout.addWidget(self.spinBox_zoom)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.toolButton_fit_img = QToolButton(self.widget)
        self.toolButton_fit_img.setObjectName(u"toolButton_fit_img")
        icon = QIcon()
        icon.addFile(u":/vsicons/vscode-codicons/screen-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_fit_img.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButton_fit_img)

        self.horizontalSpacer_4 = QSpacerItem(120, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.pushButton_type_polygon = QPushButton(self.widget)
        self.buttonGroup_type = QButtonGroup(MainWindow)
        self.buttonGroup_type.setObjectName(u"buttonGroup_type")
        self.buttonGroup_type.addButton(self.pushButton_type_polygon)
        self.pushButton_type_polygon.setObjectName(u"pushButton_type_polygon")
        self.pushButton_type_polygon.setCheckable(True)

        self.horizontalLayout.addWidget(self.pushButton_type_polygon)

        self.pushButton_type_bbox = QPushButton(self.widget)
        self.buttonGroup_type.addButton(self.pushButton_type_bbox)
        self.pushButton_type_bbox.setObjectName(u"pushButton_type_bbox")
        self.pushButton_type_bbox.setCheckable(True)
        self.pushButton_type_bbox.setChecked(True)

        self.horizontalLayout.addWidget(self.pushButton_type_bbox)

        self.pushButton_type_keypoint = QPushButton(self.widget)
        self.buttonGroup_type.addButton(self.pushButton_type_keypoint)
        self.pushButton_type_keypoint.setObjectName(u"pushButton_type_keypoint")
        self.pushButton_type_keypoint.setCheckable(True)

        self.horizontalLayout.addWidget(self.pushButton_type_keypoint)

        self.horizontalSpacer_3 = QSpacerItem(1070, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.pushButton_capture = QPushButton(self.widget)
        self.pushButton_capture.setObjectName(u"pushButton_capture")

        self.horizontalLayout.addWidget(self.pushButton_capture)

        self.pushButton_prev_img = QPushButton(self.widget)
        self.pushButton_prev_img.setObjectName(u"pushButton_prev_img")

        self.horizontalLayout.addWidget(self.pushButton_prev_img)

        self.pushButton_next_img = QPushButton(self.widget)
        self.pushButton_next_img.setObjectName(u"pushButton_next_img")

        self.horizontalLayout.addWidget(self.pushButton_next_img)


        self.verticalLayout_2.addWidget(self.widget)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.graphicsView = QGraphicsView(self.splitter)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(600, 0))
        self.splitter.addWidget(self.graphicsView)
        self.groupBox = QGroupBox(self.splitter)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButton_rm = QToolButton(self.groupBox)
        self.toolButton_rm.setObjectName(u"toolButton_rm")
        icon1 = QIcon()
        icon1.addFile(u":/vsicons/vscode-codicons/trash.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_rm.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.toolButton_rm)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.comboBox_show_count = QComboBox(self.groupBox)
        self.comboBox_show_count.addItem("")
        self.comboBox_show_count.addItem("")
        self.comboBox_show_count.addItem("")
        self.comboBox_show_count.setObjectName(u"comboBox_show_count")

        self.horizontalLayout_2.addWidget(self.comboBox_show_count)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.toolButton_prev_page = QToolButton(self.groupBox)
        self.toolButton_prev_page.setObjectName(u"toolButton_prev_page")

        self.horizontalLayout_2.addWidget(self.toolButton_prev_page)

        self.label_page = QLabel(self.groupBox)
        self.label_page.setObjectName(u"label_page")

        self.horizontalLayout_2.addWidget(self.label_page)

        self.toolButton_next_page = QToolButton(self.groupBox)
        self.toolButton_next_page.setObjectName(u"toolButton_next_page")

        self.horizontalLayout_2.addWidget(self.toolButton_next_page)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.checkBox_show_all = QCheckBox(self.groupBox)
        self.checkBox_show_all.setObjectName(u"checkBox_show_all")

        self.horizontalLayout_3.addWidget(self.checkBox_show_all)

        self.checkBox_showlabel = QCheckBox(self.groupBox)
        self.checkBox_showlabel.setObjectName(u"checkBox_showlabel")
        self.checkBox_showlabel.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_showlabel)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_4.addWidget(self.label_5)

        self.lineEdit_detector = QLineEdit(self.groupBox)
        self.lineEdit_detector.setObjectName(u"lineEdit_detector")

        self.horizontalLayout_4.addWidget(self.lineEdit_detector)

        self.toolButton_detector_script = QToolButton(self.groupBox)
        self.toolButton_detector_script.setObjectName(u"toolButton_detector_script")

        self.horizontalLayout_4.addWidget(self.toolButton_detector_script)

        self.pushButton_detect = QPushButton(self.groupBox)
        self.pushButton_detect.setObjectName(u"pushButton_detect")

        self.horizontalLayout_4.addWidget(self.pushButton_detect)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.tableWidget_history = QTableWidget(self.groupBox)
        self.tableWidget_history.setObjectName(u"tableWidget_history")

        self.verticalLayout.addWidget(self.tableWidget_history)

        self.splitter.addWidget(self.groupBox)

        self.verticalLayout_2.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1297, 33))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        self.menuedit = QMenu(self.menubar)
        self.menuedit.setObjectName(u"menuedit")
        self.menuscripts = QMenu(self.menubar)
        self.menuscripts.setObjectName(u"menuscripts")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menuedit.menuAction())
        self.menubar.addAction(self.menuscripts.menuAction())
        self.menu.addAction(self.actionopen)
        self.menu.addAction(self.actionopen_dir)
        self.menu.addAction(self.actionexport)
        self.menu.addAction(self.actionview_db_images)
        self.menu.addAction(self.actionopen_camera)
        self.menuedit.addAction(self.actionnext_new_image)
        self.menuedit.addAction(self.actionend_image)
        self.menuedit.addAction(self.actiongoto)
        self.menuedit.addSeparator()
        self.menuedit.addAction(self.actionremove_image)
        self.menuedit.addSeparator()
        self.menuedit.addAction(self.actionfind_replace)
        self.menuscripts.addAction(self.actionadd_script)
        self.menuscripts.addSeparator()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionopen.setText(QCoreApplication.translate("MainWindow", u"open", None))
        self.actionopen_dir.setText(QCoreApplication.translate("MainWindow", u"open dir", None))
        self.actionexport.setText(QCoreApplication.translate("MainWindow", u"export", None))
        self.actionview_db_images.setText(QCoreApplication.translate("MainWindow", u"view db images", None))
        self.actionnext_new_image.setText(QCoreApplication.translate("MainWindow", u"next new image", None))
        self.actionend_image.setText(QCoreApplication.translate("MainWindow", u"end image", None))
        self.actionopen_camera.setText(QCoreApplication.translate("MainWindow", u"open camera", None))
        self.actionclose_camera.setText(QCoreApplication.translate("MainWindow", u"close camera", None))
        self.actiongoto.setText(QCoreApplication.translate("MainWindow", u"goto", None))
        self.actionremove_image.setText(QCoreApplication.translate("MainWindow", u"remove image", None))
        self.actionset_train_script.setText(QCoreApplication.translate("MainWindow", u"set train script", None))
        self.actionstart_train.setText(QCoreApplication.translate("MainWindow", u"start train", None))
        self.actionadd_script.setText(QCoreApplication.translate("MainWindow", u"add script", None))
        self.actionfind_replace.setText(QCoreApplication.translate("MainWindow", u"find and replace", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"zoom:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.toolButton_fit_img.setText(QCoreApplication.translate("MainWindow", u"fit", None))
        self.pushButton_type_polygon.setText(QCoreApplication.translate("MainWindow", u"polygon", None))
        self.pushButton_type_bbox.setText(QCoreApplication.translate("MainWindow", u"bbox", None))
        self.pushButton_type_keypoint.setText(QCoreApplication.translate("MainWindow", u"keypoint", None))
#if QT_CONFIG(tooltip)
        self.pushButton_capture.setToolTip(QCoreApplication.translate("MainWindow", u"capture from opened capture", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_capture.setText(QCoreApplication.translate("MainWindow", u"capture", None))
        self.pushButton_prev_img.setText(QCoreApplication.translate("MainWindow", u"back", None))
        self.pushButton_next_img.setText(QCoreApplication.translate("MainWindow", u"next", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"annotations", None))
        self.toolButton_rm.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"per page\uff1a", None))
        self.comboBox_show_count.setItemText(0, QCoreApplication.translate("MainWindow", u"50", None))
        self.comboBox_show_count.setItemText(1, QCoreApplication.translate("MainWindow", u"100", None))
        self.comboBox_show_count.setItemText(2, QCoreApplication.translate("MainWindow", u"200", None))

        self.label_4.setText("")
        self.toolButton_prev_page.setText(QCoreApplication.translate("MainWindow", u"|<", None))
        self.label_page.setText(QCoreApplication.translate("MainWindow", u"1/1", None))
        self.toolButton_next_page.setText(QCoreApplication.translate("MainWindow", u">|", None))
        self.checkBox_show_all.setText(QCoreApplication.translate("MainWindow", u"show all", None))
        self.checkBox_showlabel.setText(QCoreApplication.translate("MainWindow", u"show label", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"script detector", None))
        self.toolButton_detector_script.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.pushButton_detect.setToolTip(QCoreApplication.translate("MainWindow", u"capture from opened capture", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_detect.setText(QCoreApplication.translate("MainWindow", u"detect", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"file", None))
        self.menuedit.setTitle(QCoreApplication.translate("MainWindow", u"edit", None))
        self.menuscripts.setTitle(QCoreApplication.translate("MainWindow", u"scripts", None))
    # retranslateUi

