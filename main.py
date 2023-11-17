from PySide6.QtWidgets import *
from PySide6.QtCore import *
from pynput import keyboard
from mainUI import Ui_MainWindow
import sys
import paho.mqtt.client as mqtt


class KeyThread(QThread):
    UP = False
    DOWN = False
    LEFT = False
    RIGHT = False

    cmdSignal = Signal(str)
    exitSignal = Signal()

    def __init__(self):
        super().__init__()

    def on_press(self, key):
        if key == keyboard.Key.up and not self.UP:
            self.UP = True
            self.cmdSignal.emit('GO')
        if key == keyboard.Key.down and not self.DOWN:
            self.DOWN = True
            self.cmdSignal.emit('BACK')
        if key == keyboard.Key.left and not self.LEFT:
            self.LEFT = True
            self.cmdSignal.emit('LEFT')
        if key == keyboard.Key.right and not self.RIGHT:
            self.RIGHT = True
            self.cmdSignal.emit('RIGHT')

    def on_release(self, key):
        if key == keyboard.Key.up and self.UP:
            self.UP = False
            self.cmdSignal.emit('STOP')
        if key == keyboard.Key.down and self.DOWN:
            self.DOWN = False
            self.cmdSignal.emit('STOP')
        if key == keyboard.Key.left and self.LEFT:
            self.LEFT = False
            self.cmdSignal.emit('MID')
        if key == keyboard.Key.right and self.RIGHT:
            self.RIGHT = False
            self.cmdSignal.emit('MID')
        #     종료 시그널
        if key == keyboard.Key.esc:
            self.exitSignal.emit()

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


class MyApp(QMainWindow, Ui_MainWindow):
    broker_address = ""
    set_mqtt = False

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def ip_commit(self):
        self.mqttc = mqtt.Client("cmd_pub")
        self.mqttc.connect(self.broker_address, 1883)

        if not self.set_mqtt:
            self.keyThread = KeyThread()
            self.keyThread.start()
            self.keyThread.cmdSignal.connect(self.pub_message)
            self.keyThread.exitSignal.connect(self.close)

        self.set_mqtt = True

    def ip_changed(self, val):
        self.broker_address = val

    def pub_message(self, msg):
        if self.set_mqtt:
            self.mqttc.publish("command", msg)

    def close_event(self, event):
        # thread close
        self.keyThread.terminate()
        self.close()


if __name__ == '__main__':
    app = QApplication()
    win = MyApp()
    win.show()
    # app.exec()
    sys.exit(app.exec())
