from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import mysql.connector
from threading import Timer
from time import sleep
import signal
from PySide6.QtCore import *
import cv2
import sys


class CmdThread(QThread):
    speed = 100

    def __init__(self):
        super().__init__()
        self.db = mysql.connector.connect(host='52.78.74.11', user='ondol', password='1234', database='rc_car',
                                          auth_plugin='mysql_native_password')
        self.cur = self.db.cursor()
        self.ready = None
        self.timer = None
        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.myMotor = self.mh.getMotor(2)
        self.pwm = PWM(0x6f)
        self.pwm.setPWMFreq(60)
        signal.signal(signal.SIGINT, self.close_db)
        self.polling()

    def run(self):
        while True:
            sleep(0.1)
            if self.ready == None:
                continue

            cmd, arg = self.ready
            self.ready = None

            if cmd == "GO":
                self.go()
            if cmd == "BACK":
                self.back()
            if cmd == "STOP":
                self.stop()
            if cmd == "LEFT":
                self.left()
            if cmd == "MID":
                self.mid()
            if cmd == "RIGHT":
                self.right()

    def polling(self):
        self.cur.execute("select * from command where is_finish = 0 order by time desc")
        ids = []
        for (pk, time, cmd_string, arg_string, is_finish) in self.cur:
            if is_finish == 1:
                break
            self.ready = (cmd_string, arg_string)
            ids.append(str(pk))

        if len(ids) > 0:
            self.cur.execute("update command set is_finish = 1 where id in (" + ', '.join(ids) + ")")

        self.db.commit()
        self.timer = Timer(0.1, self.polling)
        self.timer.start()

    def close_db(self):
        print("BYE")
        self.mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
        self.cur.close()
        self.db.close()
        self.timer.cancel()
        sys.exit(0)

    def go(self):
        self.myMotor.setSpeed(self.speed)
        self.myMotor.run(Raspi_MotorHAT.BACKWARD)

    def back(self):
        self.myMotor.setSpeed(self.speed)
        self.myMotor.run(Raspi_MotorHAT.FORWARD)

    def stop(self):
        self.myMotor.setSpeed(self.speed)
        self.myMotor.run(Raspi_MotorHAT.RELEASE)

    def left(self):
        self.pwm.setPWM(0, 0, 300)

    def mid(self):
        self.pwm.setPWM(0, 0, 375)

    def right(self):
        self.pwm.setPWM(0, 0, 450)


class CameraThread(QThread):
    def __init__(self):
        super().__init__()
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, 680)
        self.camera.set(4, 480)

    def run(self):
        while self.camera.isOpened():
            _, image = self.camera.read()
            image = cv2.flip(image, -1)
            cv2.imshow('camera', image)

            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()
