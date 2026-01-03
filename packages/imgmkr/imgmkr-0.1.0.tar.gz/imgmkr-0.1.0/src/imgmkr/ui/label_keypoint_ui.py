# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'label_keypoint.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(283, 308)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.label_range = QLabel(Form)
        self.label_range.setObjectName(u"label_range")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_range.sizePolicy().hasHeightForWidth())
        self.label_range.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label_range)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_2.addWidget(self.lineEdit)

        self.comboBox = QComboBox(Form)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_2.addWidget(self.comboBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.listWidget = QListWidget(Form)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout.addWidget(self.listWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_confirm = QPushButton(Form)
        self.pushButton_confirm.setObjectName(u"pushButton_confirm")

        self.horizontalLayout_3.addWidget(self.pushButton_confirm)

        self.pushButton_cancle = QPushButton(Form)
        self.pushButton_cancle.setObjectName(u"pushButton_cancle")

        self.horizontalLayout_3.addWidget(self.pushButton_cancle)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u4f4d\u7f6e", None))
        self.label_range.setText(QCoreApplication.translate("Form", u"[0,0]", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u6807\u8bb0", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"\u53ef\u89c1", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"\u4e0d\u53ef\u89c1", None))

        self.label_4.setText(QCoreApplication.translate("Form", u"\u5386\u53f2", None))
        self.pushButton_confirm.setText(QCoreApplication.translate("Form", u"confirm", None))
        self.pushButton_cancle.setText(QCoreApplication.translate("Form", u"cancle", None))
    # retranslateUi

