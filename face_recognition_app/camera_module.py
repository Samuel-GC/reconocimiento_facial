import cv2
import numpy as np
from kivy.graphics.texture import Texture

# Import PiCamera only if running on Raspberry Pi
try:
    from picamera2 import Picamera2
    from libcamera import Transform
    RASPBERRY_PI_AVAILABLE = True
    print("Depuración: Picamera2 importado correctamente")
except ImportError:
    RASPBERRY_PI_AVAILABLE = False
    print(f"Depuración: Error al importar Picamera2: {e}")

class CameraModule:
    def __init__(self, use_pi_camera=True):
        self.use_pi_camera = use_pi_camera
        print(f"Depuración: use_pi_camera={self.use_pi_camera}, RASPBERRY_PI_AVAILABLE={RASPBERRY_PI_AVAILABLE}")
        self.capture = None

        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            print("Depuración: Usando Picamera2")
            self.camera = Picamera2()
            config = self.camera.create_still_configuration(main={"size": (640, 480)},
                                                            transform=Transform(hflip=1))
            self.camera.configure(config)
        else:
            print("Depuración: Usando cv2.VideoCapture")
            self.capture = cv2.VideoCapture(0)

    def start(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            self.camera.start()
        else:
            if self.capture is None or not self.capture.isOpened():
                self.capture = cv2.VideoCapture(0)
                if not self.capture.isOpened():
                    raise Exception("Cannot open camera")

    def stop(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            self.camera.close()
        else:
            if self.capture:
                self.capture.release()
                self.capture = None

    def get_frame(self):
        if self.use_pi_camera and RASPBERRY_PI_AVAILABLE:
            try:
                frame = self.camera.capture_array()
                if frame is None:
                    print("Depuración: El frame capturado es None")
                else:
                    print("Depuración: Dimensiones del frame capturado:", frame.shape)
                return frame
            except Exception as e:
                print("Error al capturar el frame:", e)
                return None
        else:
            if self.capture:
                ret, frame = self.capture.read()
                if ret:
                    return frame
                else:
                    print("Depuración: No se pudo leer el frame del dispositivo de captura")
            else:
                print("Depuración: El dispositivo de captura es None")
            return None

    def convert_frame_to_texture(self, frame):
        if frame is None:
            print("Depuración: El frame pasado a convert_frame_to_texture es None")
            return None
        try:
            # Convertir el frame de BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = frame_rgb.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            print("Depuración: Textura creada con tamaño:", texture.size)
            return texture
        except Exception as e:
            print("Error al convertir el frame a textura:", e)
            return None




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
