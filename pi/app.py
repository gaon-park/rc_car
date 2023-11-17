from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
from PySide2.QtCore import *
import cv2
import paho.mqtt.client as mqtt
import socket


class CmdThread(QThread):
    broker_address = "127.0.0.1"
    speed = 100

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
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

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("cmd_sub")
        print(self.broker_address)
        self.client.connect(self.broker_address)
        self.client.subscribe("command")
        self.client.on_message = self.on_command

        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.myMotor = self.mh.getMotor(2)
        self.pwm = PWM(0x6f)
        self.pwm.setPWMFreq(60)

    def run(self):
        self.client.loop_forever()

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
        self.camera.set(3, 640)
        self.camera.set(4, 480)

    def run(self):
        while self.camera.isOpened():
            _, image = self.camera.read()
            image = cv2.flip(image, -1)
            cv2.imshow('camera test', image)

            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destoryAllWindows()


if __name__ == '__main__':
    cameraTh = CameraThread()
    cameraTh.start()
    cmdTh = CmdThread()
    cmdTh.start()

