# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPlainTextEdit,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.logText = QPlainTextEdit(self.centralwidget)
        self.logText.setObjectName(u"logText")
        self.logText.setGeometry(QRect(10, 10, 311, 331))
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(8)
        self.logText.setFont(font)
        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setGeometry(QRect(480, 390, 71, 71))
        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setGeometry(QRect(550, 390, 71, 71))
        self.leftButton = QPushButton(self.centralwidget)
        self.leftButton.setObjectName(u"leftButton")
        self.leftButton.setGeometry(QRect(70, 410, 71, 41))
        self.rightButton = QPushButton(self.centralwidget)
        self.rightButton.setObjectName(u"rightButton")
        self.rightButton.setGeometry(QRect(210, 410, 71, 41))
        self.midButton = QPushButton(self.centralwidget)
        self.midButton.setObjectName(u"midButton")
        self.midButton.setGeometry(QRect(140, 410, 71, 41))
        self.backButton = QPushButton(self.centralwidget)
        self.backButton.setObjectName(u"backButton")
        self.backButton.setGeometry(QRect(140, 450, 71, 41))
        self.goButton = QPushButton(self.centralwidget)
        self.goButton.setObjectName(u"goButton")
        self.goButton.setGeometry(QRect(140, 370, 71, 41))
        self.sensingText = QPlainTextEdit(self.centralwidget)
        self.sensingText.setObjectName(u"sensingText")
        self.sensingText.setGeometry(QRect(330, 10, 461, 331))
        self.sensingText.setFont(font)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stopButton.clicked.connect(MainWindow.stop)
        self.startButton.clicked.connect(MainWindow.start)
        self.rightButton.clicked.connect(MainWindow.right)
        self.backButton.clicked.connect(MainWindow.back)
        self.leftButton.clicked.connect(MainWindow.left)
        self.goButton.clicked.connect(MainWindow.go)
        self.midButton.clicked.connect(MainWindow.mid)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.logText.setPlainText("")
        self.logText.setReadOnly(True)
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"STOP", None))
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"START", None))
        self.leftButton.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.rightButton.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.midButton.setText(QCoreApplication.translate("MainWindow", u"Mid", None))
        self.backButton.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.goButton.setText(QCoreApplication.translate("MainWindow", u"Go", None))
        self.sensingText.setPlainText("")
        self.sensingText.setReadOnly(True)
    # retranslateUi

