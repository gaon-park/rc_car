from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import paho.mqtt.client as mqtt
import socket
from sense_hat import SenseHat
from gpiozero import TonalBuzzer
import io
import logging
import socketserver
from http import server
from threading import Condition
import threading
from PySide2.QtCore import *

# camera
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera

# oled
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

IS_FRONT = False
IS_BACK = False
IS_LEFT = False
IS_RIGHT = False
CMD_CNT = 0
PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        global output
        global PAGE
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class SenseHatThread(threading.Thread):
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

    def on_dir_led(self, arg):
        for pos in arg:
            self.sense.set_pixel(pos[0], pos[1], self.YELLOW)

    def on_break_led(self):
        self.sense.set_pixel(7, 7, self.RED)
        self.sense.set_pixel(7, 0, self.RED)

    current_cnt = 0

    def run(self):
        global IS_FRONT, IS_BACK, IS_LEFT, IS_RIGHT, CMD_CNT
        while True:
            if self.current_cnt != CMD_CNT:
                self.sense.clear()
                self.current_cnt = CMD_CNT
            if IS_FRONT and IS_LEFT:
                self.on_dir_led(self.FRONT_LEFT)
            elif IS_FRONT and IS_RIGHT:
                self.on_dir_led(self.FRONT_RIGHT)
            elif IS_BACK and IS_LEFT:
                self.on_dir_led(self.BACK_LEFT)
            elif IS_BACK and IS_RIGHT:
                self.on_dir_led(self.BACK_RIGHT)
            elif IS_FRONT:
                self.on_dir_led(self.FRONT)
            elif IS_BACK:
                self.on_dir_led(self.BACK)
            elif IS_LEFT:
                self.on_dir_led(self.LEFT)
            elif IS_RIGHT:
                self.on_dir_led(self.RIGHT)
            else:
                self.on_break_led()


class EtcThread(threading.Thread):
    broker_address = socket.gethostbyname(socket.gethostname())
    buzzer = TonalBuzzer(14)
    lst = 810.2

    speed_cmd_signal = Signal()

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


class CmdThread(threading.Thread):
    broker_address = socket.gethostbyname(socket.gethostname())
    speed = 50  # default speed = 50, 이후 mqtt command 에 따라 50씩 증가

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        global IS_FRONT, IS_BACK, IS_LEFT, IS_RIGHT, CMD_CNT
        CMD_CNT += 1
        if "go" == cmd and not IS_FRONT:
            IS_FRONT = True
            IS_BACK = False
            self.go()
        elif "back" == cmd and not IS_BACK:
            IS_FRONT = False
            IS_BACK = True
            self.back()
        elif "stop" == cmd and (IS_FRONT or IS_BACK):
            IS_FRONT = False
            IS_BACK = False
            self.stop()
        elif "left" == cmd and not IS_LEFT:
            IS_LEFT = True
            IS_RIGHT = False
            self.left()
        elif "right" == cmd and not IS_RIGHT:
            IS_LEFT = False
            IS_RIGHT = True
            self.right()
        elif "mid" == cmd and (IS_LEFT or IS_RIGHT):
            IS_LEFT = False
            IS_RIGHT = False
            self.mid()
        elif "speed" in cmd:
            self.speed = int(cmd.split("=")[1]) * 50
            self.speed_changed()

    def speed_changed(self):
        if IS_FRONT:
            self.go()
        elif IS_BACK:
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


class CameraThread(threading.Thread):
    def __init__(self):
        global output
        super().__init__()
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.configure(self.picam2.create_video_configuration(transform=libcamera.Transform(hflip=1, vflip=1)))

        self.picam2.start_recording(JpegEncoder(), FileOutput(output))

    def run(self):
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            self.picam2.stop_recording()


class LCDThread(threading.Thread):
    broker_address = socket.gethostbyname(socket.gethostname())
    font = ImageFont.truetype('malgun.ttf', 25)
    WIDTH = 128
    HEIGHT = 64
    BORDER = 5

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("lcd_sub")
        self.client.connect(self.broker_address)
        self.client.subscribe("lcd")
        self.client.on_message = self.on_command

        self.oled_reset = digitalio.DigitalInOut(board.D27)

        # use for spi
        self.spi = board.SPI()
        self.oled_cs = digitalio.DigitalInOut(board.D8)
        self.oled_dc = digitalio.DigitalInOut(board.D26)
        self.oled = adafruit_ssd1306.SSD1306_SPI(self.WIDTH, self.HEIGHT, self.spi, self.oled_dc, self.oled_reset, self.oled_cs)

        self.display("Hello world")

    def on_command(self, client, userdata, message):
        self.display(str(message.payload.decode("utf-8")))

    def display(self, data):
        # clear
        self.oled.fill(0)
        self.oled.show()

        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)
        draw.rectangle(
            (self.BORDER, self.BORDER, self.oled.width - self.BORDER - 1, self.oled.height - self.BORDER - 1),
            outline=0,
            fill=0
        )

        draw.text((10, 10), data, font=self.font, fill=1)  # 하얀색 폰트인 글씨를 (10,10) 위치에 그리기

        # 이미지 자르기
        box = (0, 0, self.WIDTH, self.HEIGHT)
        region = image.crop(box)  # 해당 영역 만큼 이미지 자르기
        # 이미지 변형
        region = region.transpose(Image.ROTATE_180)  # 180도 회전
        image.paste(region, box)

        # show
        self.oled.image(image)
        self.oled.show()

    def run(self):
        self.client.loop_forever()


output = StreamingOutput()
if __name__ == '__main__':
    camera_th = CameraThread()
    camera_th.start()
    sense_th = SenseHatThread()
    sense_th.start()
    cmd_th = CmdThread()
    cmd_th.start()
    etc_th = EtcThread()
    etc_th.start()
    lcd_th = LCDThread()
    lcd_th.start()
