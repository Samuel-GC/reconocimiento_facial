import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os

from picamera2 import Picamera2

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Múltiples Vistas")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        self.cap = None  # Inicializa self.cap aquí
        
        self.picam2 = Picamera2()
        self.config = self.picam2.create_preview_configuration(main={"size": (640, 480)})  # Conf>
        self.picam2.configure(self.config)

        self.show_main()

    def acceder(self):
        # Directorio con las imágenes
        image_folder = "D:/escritorio/reconocimiento_facial/tkinter/fotos/"
        self.known_face_encodings = {}
        for image_name in os.listdir(image_folder):
            image_path = os.path.join(image_folder, image_name)
            
            # Leer la imagen
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error al cargar {image_name}, se omitirá.")
                continue
            
            # Detectar ubicaciones de rostros en la imagen
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                print(f"No se detectaron rostros en {image_name}, se omitirá.")
                continue
            
            # Tomar la primera cara detectada (puedes modificar para múltiples caras)
            face_loc = face_locations[0]
            
            # Obtener la codificación del rostro
            face_encoding = face_recognition.face_encodings(img, known_face_locations=[face_loc])[0]
            
            # Guardar la codificación con el nombre de la imagen
            self.known_face_encodings[image_name] = face_encoding
        
        # Comprobar que se hayan cargado codificaciones
        if not self.known_face_encodings:
            print("No se encontraron codificaciones válidas.")
            return
        
        print("Codificaciones cargadas con éxito:", list(self.known_face_encodings.keys()))
    
        self.clear_frame()
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)  # Inicia la captura de la cámara web
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=20)
        self.picam2.start()
        self.update_video()  # Inicia la actualización del video en la GUI
        tk.Button(self.root, text="Regresar", command=self.show_main, height=2, width=50).pack(pady=20)

    def update_video(self):
        frame_counter = 0

        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
         
        if frame_counter % 5 == 0 or frame_counter == 0:
            frame = cv2.flip(frame, 1)
            face_locations = face_recognition.face_locations(frame)
        frame_counter += 1
        if face_locations != []:
            for face_location in face_locations:
                # Obtener codificación de la cara detectada en el frame
                face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
                
                # Comparar con todas las codificaciones conocidas
                name = "Desconocido"
                color = (50, 50, 225)
                for known_name, known_encoding in self.known_face_encodings.items():
                    result = face_recognition.compare_faces([known_encoding], face_frame_encodings, tolerance=0.6)
                    face_distance = face_recognition.face_distance([known_encoding], face_frame_encodings)[0]
                    similarity_percentage = round((1 - face_distance) * 100, 0)
                    
                    if result[0]:
                        known_name=known_name.split(".")[0]
                        name = f"{known_name} | {similarity_percentage}%"
                        color = (125, 220, 0)
                        break  # Salir del bucle si se encuentra una coincidencia
                
                # Dibujar rectángulos y texto en el frame
                cv2.rectangle(frame, (face_location[3], face_location[2]), 
                            (face_location[1], face_location[2] + 30), color, -1)
                cv2.rectangle(frame, (face_location[3], face_location[0]), 
                            (face_location[1], face_location[2]), color, 2)
                cv2.putText(frame, name, (face_location[3], face_location[2] + 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        # Convertir el frame a un formato compatible con Tkinter
        cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_img)

        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        self.video_label.after(10, self.update_video)  # Llama a la misma función después de 10 ms

    def administar(self):
        self.clear_frame()
        tk.Label(self.root, text="Administar Usuarios", font=('Helvetica', 16)).pack(pady=20)
        tk.Button(self.root, text="Regresar", command=self.show_main, height=2, width=50).pack(pady=20)

    def show_main(self):
        if self.cap and self.cap.isOpened():  # Asegúrate de liberar la cámara solo si está abierta
            self.cap.release()  # Libera la cámara web cuando regresas al menú principal
        self.clear_frame()
        tk.Button(self.root, text="Acceder", command=self.acceder, height=3, width=50).pack(pady=20)
        tk.Button(self.root, text="Administar", command=self.administar, height=3, width=50).pack(pady=20)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
