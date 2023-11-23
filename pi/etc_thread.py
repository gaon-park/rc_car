import threading
from gpiozero import TonalBuzzer
import socket
import paho.mqtt.client as mqtt
import tone_dic


class EtcThread(threading.Thread):
    BROKER_ADDRESS = socket.gethostbyname(socket.gethostname())
    buzzer = TonalBuzzer(14)

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client("etc_sub")
        self.client.connect(self.BROKER_ADDRESS)
        self.client.subscribe("etc")
        self.client.on_message = self.on_command

    def on_command(self, client, userdata, message):
        cmd = str(message.payload.decode("utf-8"))
        if "buzzer_on" == cmd:
            self.buzzer.play(tone_dic.TONE_DIC['c4'])
        elif "buzzer_off" == cmd:
            self.buzzer.stop()

    def run(self):
        self.client.loop_forever()
