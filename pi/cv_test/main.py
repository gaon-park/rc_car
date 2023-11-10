from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from mainUI import Ui_MainWindow
import cv2
import numpy
from time import sleep
import os
del os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']

class MyThread(QThread):
    mySignal = Signal(QPixmap, QPixmap)

    #Thread 시작 시 촬영
    def __init__(self):
        super().__init__()
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 480)
        self.cam.set(4, 320)

    def rotate(self, src):
        dst = cv2.flip(src, -1)
        return dst

    flag = False
    def run(self):
        self.flag = True
        while self.flag:
            ret, self.img = self.cam.read()
            self.img = self.rotate(self.img)
            if ret:
                self.printImage(self.img)
            sleep(0.1)

    def stop(self):
        self.flag = False

    def printImage(self, imgBGR):
        imgRGB = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2RGB)
        h, w, byte = imgRGB.shape
        img = QImage(imgRGB, w, h, byte*w, QImage.Format_RGB888)
        q_img1 = QPixmap(img)

        grayImg = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY)
        cannyImg = cv2.Canny(grayImg, 50, 200)
        imgRGB = cv2.cvtColor(cannyImg, cv2.COLOR_BGR2RGB)
        h, w, byte = imgRGB.shape
        img = QImage(imgRGB, w, h, byte * w, QImage.Format_RGB888)
        q_img2 = QPixmap(img)

        self.mySignal.emit(q_img1, q_img2)

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.main()

    def main(self):
        self.th = MyThread()
        self.th.mySignal.connect(self.setImage)

    def setImage(self, img, img2):
        self.cam_lbl.setPixmap(img)
        self.openCV_lbl.setPixmap(img2)

    def play(self):
        print('play')
        self.th.start()

    def mode(self):
        print('mode')

    def closeEvent(self, event):
        self.th.stop()
        #self.th.wait(3000)
        self.close()

if __name__ == '__main__':
    app = QApplication()
    win = MyApp()
    win.show()
    app.exec_()