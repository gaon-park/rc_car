import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import paho.mqtt.client as mqtt
import socket
import threading


class OLEDThread(threading.Thread):
    BROKER_ADDRESS = socket.gethostbyname(socket.gethostname())
    font = ImageFont.truetype('malgun.ttf', 25)
    WIDTH = 128
    HEIGHT = 64
    BORDER = 5

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("lcd_sub")
        self.client.connect(self.BROKER_ADDRESS)
        self.client.subscribe("lcd")
        self.client.on_message = self.on_command

        self.oled_reset = digitalio.DigitalInOut(board.D27)

        # use for spi
        self.spi = board.SPI()
        self.oled_cs = digitalio.DigitalInOut(board.D8)
        self.oled_dc = digitalio.DigitalInOut(board.D26)
        self.oled = adafruit_ssd1306.SSD1306_SPI(self.WIDTH, self.HEIGHT, self.spi, self.oled_dc, self.oled_reset,
                                                 self.oled_cs)

        self.display("Hello")

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
