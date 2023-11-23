import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera
import streaming


class CameraThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.configure(self.picam2.create_video_configuration(transform=libcamera.Transform(hflip=1, vflip=1)))
        self.picam2.start_recording(JpegEncoder(), FileOutput(streaming.output))

    def run(self):
        try:
            address = ('', 8000)
            server = streaming.StreamingServer(address, streaming.StreamingHandler)
            server.serve_forever()
        finally:
            self.picam2.stop_recording()
