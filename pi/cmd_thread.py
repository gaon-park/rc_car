from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import threading
import paho.mqtt.client as mqtt
import socket


class CmdThread(threading.Thread):
    BROKER_ADDRESS = socket.gethostbyname(socket.gethostname())
    speed_idx = 0
    speed = [100, 150, 200, 255]
    front_or_back = ""  # 현재 직진 중인가? 후진 중인가?

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("cmd_sub")
        self.client.connect(self.BROKER_ADDRESS)
        self.client.subscribe("command")
        self.client.on_message = self.on_command

        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.myMotor = self.mh.getMotor(2)
        self.pwm = PWM(0x6f)
        self.pwm.setPWMFreq(60)

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        if "go" == cmd:
            self.front_or_back = "front"
            self.go()
        elif "back" == cmd:
            self.front_or_back = "back"
            self.back()
        elif "stop" == cmd:
            self.front_or_back = ""
            self.stop()
        elif "left_max" == cmd:
            self.left_max()
        elif "left_min" == cmd:
            self.left_min()
        elif "right_max" == cmd:
            self.right_max()
        elif "right_min" == cmd:
            self.right_min()
        elif "mid" == cmd:
            self.mid()
        elif "speed" in cmd:
            idx = int(cmd.split("=")[1])
            if idx <= 2:
                self.speed_idx = 0
            elif idx <= 4:
                self.speed_idx = 1
            elif idx <= 6:
                self.speed_idx = 2
            else:
                self.speed_idx = 3
            self.speed_changed()

    def speed_changed(self):
        if self.front_or_back == "front":
            self.go()
        elif self.front_or_back == "back":
            self.back()

    def run(self):
        self.client.loop_forever()

    def go(self):
        self.myMotor.setSpeed(self.speed[self.speed_idx])
        self.myMotor.run(Raspi_MotorHAT.BACKWARD)

    def back(self):
        self.myMotor.setSpeed(self.speed[self.speed_idx])
        self.myMotor.run(Raspi_MotorHAT.FORWARD)

    def stop(self):
        self.myMotor.setSpeed(self.speed[self.speed_idx])
        self.myMotor.run(Raspi_MotorHAT.RELEASE)

    def left_max(self):
        self.pwm.setPWM(0, 0, 300)

    def left_min(self):
        self.pwm.setPWM(0, 0, 340)

    def mid(self):
        self.pwm.setPWM(0, 0, 375)

    def right_max(self):
        self.pwm.setPWM(0, 0, 450)

    def right_min(self):
        self.pwm.setPWM(0, 0, 410)
