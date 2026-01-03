# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'finder.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QToolButton, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(507, 232)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBox = QCheckBox(self.tab)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_2.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_find = QLineEdit(self.frame)
        self.lineEdit_find.setObjectName(u"lineEdit_find")

        self.horizontalLayout.addWidget(self.lineEdit_find)

        self.pushButton_find = QPushButton(self.frame)
        self.pushButton_find.setObjectName(u"pushButton_find")

        self.horizontalLayout.addWidget(self.pushButton_find)

        self.pushButton_find_prev = QPushButton(self.frame)
        self.pushButton_find_prev.setObjectName(u"pushButton_find_prev")

        self.horizontalLayout.addWidget(self.pushButton_find_prev)


        self.verticalLayout_2.addWidget(self.frame)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.toolButton_fold = QToolButton(self.tab)
        self.toolButton_fold.setObjectName(u"toolButton_fold")

        self.horizontalLayout_4.addWidget(self.toolButton_fold)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.frame_replace = QFrame(self.tab)
        self.frame_replace.setObjectName(u"frame_replace")
        self.frame_replace.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_replace.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_replace)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.frame_replace)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.lineEdit_replace = QLineEdit(self.frame_replace)
        self.lineEdit_replace.setObjectName(u"lineEdit_replace")

        self.horizontalLayout_3.addWidget(self.lineEdit_replace)

        self.pushButton_replace = QPushButton(self.frame_replace)
        self.pushButton_replace.setObjectName(u"pushButton_replace")

        self.horizontalLayout_3.addWidget(self.pushButton_replace)

        self.pushButton_replace_all = QPushButton(self.frame_replace)
        self.pushButton_replace_all.setObjectName(u"pushButton_replace_all")

        self.horizontalLayout_3.addWidget(self.pushButton_replace_all)

        self.pushButton_replace_reset = QPushButton(self.frame_replace)
        self.pushButton_replace_reset.setObjectName(u"pushButton_replace_reset")

        self.horizontalLayout_3.addWidget(self.pushButton_replace_reset)


        self.verticalLayout_2.addWidget(self.frame_replace)

        self.tabWidget.addTab(self.tab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"use regx", None))
        self.label.setText(QCoreApplication.translate("Form", u"find", None))
        self.pushButton_find.setText(QCoreApplication.translate("Form", u"next", None))
        self.pushButton_find_prev.setText(QCoreApplication.translate("Form", u"back", None))
        self.toolButton_fold.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"replace", None))
        self.pushButton_replace.setText(QCoreApplication.translate("Form", u"replace", None))
        self.pushButton_replace_all.setText(QCoreApplication.translate("Form", u"replace all", None))
        self.pushButton_replace_reset.setText(QCoreApplication.translate("Form", u"reset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"Label Finder", None))
    # retranslateUi

