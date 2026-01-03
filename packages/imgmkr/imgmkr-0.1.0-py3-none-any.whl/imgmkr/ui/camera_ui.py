# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGraphicsView, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(621, 482)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox_camera = QComboBox(Form)
        self.comboBox_camera.setObjectName(u"comboBox_camera")

        self.horizontalLayout.addWidget(self.comboBox_camera)

        self.pushButton_open = QPushButton(Form)
        self.pushButton_open.setObjectName(u"pushButton_open")

        self.horizontalLayout.addWidget(self.pushButton_open)

        self.pushButton_settings = QPushButton(Form)
        self.pushButton_settings.setObjectName(u"pushButton_settings")

        self.horizontalLayout.addWidget(self.pushButton_settings)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboBox_resolutions = QComboBox(Form)
        self.comboBox_resolutions.setObjectName(u"comboBox_resolutions")

        self.horizontalLayout.addWidget(self.comboBox_resolutions)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_capture = QPushButton(Form)
        self.pushButton_capture.setObjectName(u"pushButton_capture")

        self.horizontalLayout.addWidget(self.pushButton_capture)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.graphicsView = QGraphicsView(Form)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_open.setText(QCoreApplication.translate("Form", u"open", None))
        self.pushButton_settings.setText(QCoreApplication.translate("Form", u"settings", None))
        self.label.setText(QCoreApplication.translate("Form", u"resolutions", None))
        self.pushButton_capture.setText(QCoreApplication.translate("Form", u"capture", None))
    # retranslateUi

