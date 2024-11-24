import cv2
import numpy as np
from kivy.graphics.texture import Texture

# Import PiCamera only if running on Raspberry Pi
try:
    from picamera2 import PiCamera2
    from picamera2.array import PiRGBArray
    RASPBERRY_PI_AVAILABLE = True
except ImportError:
    RASPBERRY_PI_AVAILABLE = False

class CameraModule:
    def __init__(self, use_pi_camera=True):
        self.use_pi_camera = use_pi_camera
        self.capture = None
        self.stream = None

        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            # Initialize the PiCamera
            self.camera = PiCamera2()
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



# from picamera2 import Picamera2
# import cv2

# # Inicializa la cÃ¡mara
# picam2 = Picamera2()
# config = picam2.create_preview_configuration(main={"size": (640, 480)})  # ConfiguraciÃ³n de resoluciÃ³n
# picam2.configure(config)

# # Inicia la cÃ¡mara
# picam2.start()
# print("CÃ¡mara en funcionamiento. Presiona 'q' para salir.")

# try:
#     # Muestra una sola ventana con video en vivo
#     while True:
#         # Captura un frame de la cÃ¡mara
#         frame = picam2.capture_array()

#         # Muestra el frame en la misma ventana
#         cv2.imshow("Video en Vivo", frame)

#         # Salir del bucle si se presiona 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# except KeyboardInterrupt:
#     print("\nInterrumpido por el usuario.")

# finally:
#     # Libera recursos
#     picam2.stop()
#     cv2.destroyAllWindows()
#     print("CÃ¡mara detenida y recursos liberados.")
