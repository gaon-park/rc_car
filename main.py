from PySide6.QtWidgets import *
from PySide6.QtCore import *
from pynput import keyboard
from mainUI import Ui_MainWindow
import mysql.connector
import sys


class KeyThread(QThread):
    UP = False
    DOWN = False
    LEFT = False
    RIGHT = False

    cmdSignal = Signal(str, bool)
    exitSignal = Signal()

    def __init__(self):
        super().__init__()

    def on_press(self, key):
        if key == keyboard.Key.up and not self.UP:
            self.UP = True
            self.cmdSignal.emit('GO', True)
        if key == keyboard.Key.down and not self.DOWN:
            self.DOWN = True
            self.cmdSignal.emit('BACK', True)
        if key == keyboard.Key.left and not self.LEFT:
            self.LEFT = True
            self.cmdSignal.emit('LEFT', True)
        if key == keyboard.Key.right and not self.RIGHT:
            self.RIGHT = True
            self.cmdSignal.emit('RIGHT', True)

    def on_release(self, key):
        if key == keyboard.Key.up and self.UP:
            self.UP = False
            self.cmdSignal.emit('STOP', False)
        if key == keyboard.Key.down and self.DOWN:
            self.DOWN = False
            self.cmdSignal.emit('STOP', False)
        if key == keyboard.Key.left and self.LEFT:
            self.LEFT = False
            self.cmdSignal.emit('MID', False)
        if key == keyboard.Key.right and self.RIGHT:
            self.RIGHT = False
            self.cmdSignal.emit('MID', False)
        #     종료 시그널
        if key == keyboard.Key.esc:
            self.exitSignal.emit()

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init()

    def init(self):
        self.db = mysql.connector.connect(host='52.78.74.11', user='ondol', password='1234', database='rc_car',
                                          auth_plugin='mysql_native_password')
        self.cur = self.db.cursor()

        # timer setting
        self.timer = QTimer()
        self.timer.setInterval(500)  # 500ms
        self.timer.timeout.connect(self.polling_query)
        self.timer.start()

        self.keyThread = KeyThread()
        self.keyThread.start()
        self.keyThread.cmdSignal.connect(self.insert_command)
        self.keyThread.exitSignal.connect(self.close)

    def polling_query(self):
        self.cur.execute("select * from command order by time desc limit 15")
        self.ui.logText.clear()
        for (id, time, cmd_string, arg_string, is_finish) in self.cur:
            str = "%5d | %s | %6s | %6s | %4d" % (
                id, time.strftime("%Y%m%d %H:%M:%S"), cmd_string, arg_string, is_finish)
            self.ui.logText.appendPlainText(str)

        self.cur.execute("select * from sensing order by time desc limit 15")
        self.ui.sensingText.clear()
        for (id, time, num1, num2, num3, meta_string, is_finish) in self.cur:
            str = "%d | %s | %6s | %6s | %6s | %15s | %4d" % (
                id, time.strftime("%Y%m%d %H:%M:%S"), num1, num2, num3, meta_string, is_finish)
            self.ui.sensingText.appendPlainText(str)
        self.db.commit()

    def insert_command(self, cmd_string, arg_string):
        time = QDateTime().currentDateTime().toPython()
        is_finish = 0
        query = "insert into command(time, cmd_string, arg_string, is_finish) values (%s, %s, %s, %s)"
        value = (time, cmd_string, arg_string, is_finish)

        self.cur.execute(query, value)
        self.db.commit()

    def closeEvent(self, event):
        # delete command
        self.cur.execute("delete from command c where c.time <= now()")
        self.db.commit()

        # connection close
        self.cur.close()
        self.db.close()

        # thread / timer stop
        self.timer.stop()
        self.keyThread.terminate()
        self.close()


if __name__ == '__main__':
    app = QApplication()
    win = MyApp()
    win.show()
    # app.exec()
    sys.exit(app.exec())
