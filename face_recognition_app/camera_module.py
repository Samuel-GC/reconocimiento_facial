# face_recognition_app/camera_module.py

import cv2
from kivy.graphics.texture import Texture

class CameraModule:
    def __init__(self):
        self.capture = None

    def start(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            raise Exception("Cannot open camera")

    def stop(self):
        if self.capture:
            self.capture.release()
            self.capture = None

    def get_frame(self):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 1)
                return frame
        return None

    def convert_frame_to_texture(self, frame):
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture
