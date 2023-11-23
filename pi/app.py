import camera_thread
import cmd_thread
import etc_thread
import oled_thread
import sensehat_thread


if __name__ == '__main__':
    camera_th = camera_thread.CameraThread()
    camera_th.start()
    sense_th = sensehat_thread.SenseHatThread()
    sense_th.start()
    cmd_th = cmd_thread.CmdThread()
    cmd_th.start()
    etc_th = etc_thread.EtcThread()
    etc_th.start()
    oled_th = oled_thread.OLEDThread()
    oled_th.start()
