import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from kivy.graphics.texture import Texture

class CameraModule:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30
        self.raw_capture = PiRGBArray(self.camera, size=(640, 480))
        self.stream = None

    def start(self):
        self.stream = self.camera.capture_continuous(
            self.raw_capture, format="bgr", use_video_port=True
        )

    def stop(self):
        if self.stream:
            self.stream.close()
        self.camera.close()

    def get_frame(self):
        if self.stream:
            for frame in self.stream:
                image = frame.array
                self.raw_capture.truncate(0)
                return cv2.flip(image, 1)
        return None

    def convert_frame_to_texture(self, frame):
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture
