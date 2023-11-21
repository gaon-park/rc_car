from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
from PySide2.QtCore import *
import cv2
import paho.mqtt.client as mqtt
import socket
from sense_hat import SenseHat
from gpiozero import TonalBuzzer

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


class EtcThread(QThread):
    broker_address = socket.gethostbyname(socket.gethostname())
    buzzer = TonalBuzzer(14)
    lst = 810.2

    speedCmdSignal = Signal()

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("etc_sub")
        self.client.connect(self.broker_address)
        self.client.subscribe("etc")
        self.client.on_message = self.on_command

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        if "buzzer_on" == cmd:
            self.buzzer.play(self.lst)
        elif "buzzer_off" == cmd:
            self.buzzer.stop()

    def run(self):
        self.client.loop_forever()


class CmdThread(QThread):
    broker_address = socket.gethostbyname(socket.gethostname())
    speed = 50  # default speed = 50, 이후 mqtt command 에 따라 50씩 증가

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        global isFront, isBack, isLeft, isRight, cmdCnt
        cmdCnt += 1
        if "go" == cmd and not isFront:
            isFront = True
            isBack = False
            self.go()
        elif "back" == cmd and not isBack:
            isFront = False
            isBack = True
            self.back()
        elif "stop" == cmd and (isFront or isBack):
            isFront = False
            isBack = False
            self.stop()
        elif "left" == cmd and not isLeft:
            isLeft = True
            isRight = False
            self.left()
        elif "right" == cmd and not isRight:
            isLeft = False
            isRight = True
            self.right()
        elif "mid" == cmd and (isLeft or isRight):
            isLeft = False
            isRight = False
            self.mid()
        elif "speed" in cmd:
            self.speed = int(cmd.split("=")[1]) * 50
            self.speed_changed()

    def speed_changed(self):
        if isFront:
            self.go()
        elif isBack:
            self.back()

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("cmd_sub")
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
    etcTh = EtcThread()
    etcTh.start()
