from sense_hat import SenseHat
import threading
import paho.mqtt.client as mqtt
import socket


class SenseHatThread(threading.Thread):
    BROKER_ADDRESS = socket.gethostbyname(socket.gethostname())
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

    IS_FRONT = False
    IS_BACK = False
    IS_LEFT = False
    IS_RIGHT = False

    def __init__(self):
        super().__init__()
        self.sense = SenseHat()
        self.client = mqtt.Client("sensehat_sub")
        self.client.connect(self.BROKER_ADDRESS)
        self.client.subscribe("command")
        self.client.on_message = self.on_command

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        self.sense.clear()
        if "go" == cmd:
            if self.IS_LEFT:
                self.on_dir_led(self.FRONT_LEFT)
            elif self.IS_RIGHT:
                self.on_dir_led(self.FRONT_RIGHT)
            else:
                self.on_dir_led(self.FRONT)
            self.IS_FRONT = True
            self.IS_BACK = False
        elif "back" == cmd:
            if self.IS_LEFT:
                self.on_dir_led(self.BACK_LEFT)
            elif self.IS_RIGHT:
                self.on_dir_led(self.BACK_RIGHT)
            else:
                self.on_dir_led(self.BACK)
            self.IS_FRONT = False
            self.IS_BACK = True
        elif "stop" == cmd:
            self.IS_FRONT = False
            self.IS_BACK = False
            if self.IS_LEFT:
                self.on_dir_led(self.LEFT)
            elif self.IS_RIGHT:
                self.on_dir_led(self.RIGHT)
            else:
                self.on_break_led()
        elif "left" in cmd:
            if self.IS_FRONT:
                self.on_dir_led(self.FRONT_LEFT)
            elif self.IS_BACK:
                self.on_dir_led(self.BACK_LEFT)
            else:
                self.on_dir_led(self.LEFT)
            self.IS_LEFT = True
            self.IS_RIGHT = False
        elif "right" in cmd:
            if self.IS_FRONT:
                self.on_dir_led(self.FRONT_RIGHT)
            elif self.IS_BACK:
                self.on_dir_led(self.BACK_RIGHT)
            else:
                self.on_dir_led(self.RIGHT)
            self.IS_LEFT = False
            self.IS_RIGHT = True
        elif "mid" == cmd:
            self.IS_LEFT = False
            self.IS_RIGHT = False
            if self.IS_FRONT:
                self.on_dir_led(self.FRONT)
            elif self.IS_BACK:
                self.on_dir_led(self.BACK)
            else:
                self.on_break_led()

    def on_dir_led(self, arg):
        for pos in arg:
            self.sense.set_pixel(pos[0], pos[1], self.YELLOW)

    def on_break_led(self):
        self.sense.set_pixel(7, 7, self.RED)
        self.sense.set_pixel(7, 0, self.RED)

    def run(self):
        self.sense.clear()
        self.on_break_led()
        self.client.loop_forever()

