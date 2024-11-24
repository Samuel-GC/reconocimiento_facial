import cv2
import numpy as np
from kivy.graphics.texture import Texture

# Import PiCamera only if running on Raspberry Pi
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    RASPBERRY_PI_AVAILABLE = True
except ImportError:
    RASPBERRY_PI_AVAILABLE = False

class CameraModule:
    def __init__(self, use_pi_camera=False):
        self.use_pi_camera = use_pi_camera
        self.capture = None
        self.stream = None

        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            # Initialize the PiCamera
            self.camera = PiCamera()
            self.camera.resolution = (640, 480)
            self.camera.framerate = 30
            self.raw_capture = PiRGBArray(self.camera, size=(640, 480))
        else:
            # Initialize the USB/Laptop camera
            self.capture = cv2.VideoCapture(0)

    def start(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            self.stream = self.camera.capture_continuous(
                self.raw_capture, format="bgr", use_video_port=True
            )
        else:
            if self.capture is None:
                self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise Exception("Cannot open camera")

    def stop(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            if self.stream:
                self.stream.close()
            self.camera.close()
        else:
            if self.capture:
                self.capture.release()
                self.capture = None

    def get_frame(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            for frame in self.stream:
                image = frame.array
                self.raw_capture.truncate(0)
                return cv2.flip(image, 1)
        else:
            if self.capture:
                ret, frame = self.capture.read()
                if ret:
                    return cv2.flip(frame, 1)
        return None

    def convert_frame_to_texture(self, frame):
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture
