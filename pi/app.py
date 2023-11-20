from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
from PySide2.QtCore import *
import cv2
import paho.mqtt.client as mqtt
import socket
from sense_hat import SenseHat

isFront = False
isBack = False
isLeft = False
isRight = False
cmdCnt = 0

class SenseHatThread(QThread):
    def __init__(self):
        super().__init__()
        self.sense = SenseHat()

    def run(self):
        self.sense.clear()

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    FRONT = [
        [0, 3], [0, 4],
        [1, 2], [1, 3], [1, 4], [1, 5],
        [2, 3], [2, 4],
        [3, 3], [3, 4]
    ]
    BACK = [
        [4, 3], [4, 4],
        [5, 3], [5, 4],
        [6, 2], [6, 3], [6, 4], [6, 5],
        [7, 3], [7, 4]
    ]
    LEFT = [
        [3, 4], [4, 4],
        [3, 5], [4, 5],
        [2, 6], [3, 6], [4, 6], [5, 6],
        [3, 7], [4, 7]
    ]
    RIGHT = [
        [3, 0], [4, 0],
        [2, 1], [3, 1], [4, 1], [5, 1],
        [3, 2], [4, 2],
        [3, 3], [4, 3]
    ]
    FRONT_LEFT = [
        [0, 7],
        [0, 6], [1, 7],
        [0, 5], [1, 6], [2, 7],
        [2, 5],
        [3, 4]
    ]
    FRONT_RIGHT = [
        [0, 0],
        [0, 1], [1, 0],
        [0, 2], [1, 1], [2, 0],
        [2, 2],
        [3, 3]
    ]
    BACK_LEFT = [
        [7, 7],
        [6, 7], [7, 6],
        [5, 7], [6, 6], [7, 5],
        [5, 5],
        [4, 4]
    ]
    BACK_RIGHT = [
        [7, 0],
        [6, 0], [7, 1],
        [5, 0], [6, 1], [7, 2],
        [5, 2],
        [4, 3]
    ]

    def onDirLED(self, arg):
        for pos in arg:
            self.sense.set_pixel(pos[0], pos[1], self.YELLOW)

    def onBreakLED(self):
        self.sense.set_pixel(7, 7, self.RED)
        self.sense.set_pixel(7, 0, self.RED)

    currentCnt = 0
    def run(self):
        global isFront, isBack, isLeft, isRight, cmdCnt
        while True:
            if self.currentCnt != cmdCnt:
                self.sense.clear()
                self.currentCnt = cmdCnt
            if isFront and isLeft:
                self.onDirLED(self.FRONT_LEFT)
            elif isFront and isRight:
                self.onDirLED(self.FRONT_RIGHT)
            elif isBack and isLeft:
                self.onDirLED(self.BACK_LEFT)
            elif isBack and isRight:
                self.onDirLED(self.BACK_RIGHT)
            elif isFront:
                self.onDirLED(self.FRONT)
            elif isBack:
                self.onDirLED(self.BACK)
            elif isLeft:
                self.onDirLED(self.LEFT)
            elif isRight:
                self.onDirLED(self.RIGHT)
            else:
                self.onBreakLED()

class CmdThread(QThread):
    broker_address = socket.gethostbyname(socket.gethostname())
    speed = 100

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        global isFront, isBack, isLeft, isRight, cmdCnt
        cmdCnt += 1
        if "go" in cmd:
            isFront = True
            isBack = False
            self.go()
        if "back" in cmd:
            isFront = False
            isBack = True
            self.back()
        if "stop" in cmd:
            isFront = False
            isBack = False
            self.stop()
        if "left" in cmd:
            isLeft = True
            isRight = False
            self.left()
        if "right" in cmd:
            isLeft = False
            isRight = True
            self.right()
        if "mid" in cmd:
            isLeft = False
            isRight = False
            self.mid()

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
    senseTh = SenseHatThread()
    senseTh.start()
    cmdTh = CmdThread()
    cmdTh.start()

