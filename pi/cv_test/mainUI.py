# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide2.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 521)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.cam_lbl = QLabel(self.centralwidget)
        self.cam_lbl.setObjectName(u"cam_lbl")
        self.cam_lbl.setMaximumSize(QSize(480, 320))
        self.cam_lbl.setStyleSheet(u"background-color: rgb(221, 215, 255);")

        self.gridLayout.addWidget(self.cam_lbl, 0, 0, 1, 1)

        self.openCV_lbl = QLabel(self.centralwidget)
        self.openCV_lbl.setObjectName(u"openCV_lbl")
        self.openCV_lbl.setMaximumSize(QSize(480, 320))
        self.openCV_lbl.setStyleSheet(u"background-color: rgb(172, 255, 218);")

        self.gridLayout.addWidget(self.openCV_lbl, 0, 1, 1, 1)

        self.playBtn = QPushButton(self.centralwidget)
        self.playBtn.setObjectName(u"playBtn")
        self.playBtn.setMaximumSize(QSize(960, 50))
        font = QFont()
        font.setPointSize(24)
        self.playBtn.setFont(font)

        self.gridLayout.addWidget(self.playBtn, 1, 0, 1, 2)

        self.ModeBtn = QPushButton(self.centralwidget)
        self.ModeBtn.setObjectName(u"ModeBtn")
        self.ModeBtn.setMaximumSize(QSize(960, 50))
        self.ModeBtn.setFont(font)

        self.gridLayout.addWidget(self.ModeBtn, 2, 0, 1, 2)


        self.horizontalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.playBtn.clicked.connect(MainWindow.play)
        self.ModeBtn.clicked.connect(MainWindow.mode)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.cam_lbl.setText("")
        self.openCV_lbl.setText("")
        self.playBtn.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.ModeBtn.setText(QCoreApplication.translate("MainWindow", u"Mode", None))
    # retranslateUi