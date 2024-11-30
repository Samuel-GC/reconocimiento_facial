import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
from tkinter import messagebox
from datetime import datetime 
import RPi.GPIO as GPIO
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataBase.model import * 

from picamera2 import Picamera2  # Importar Picamera2


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Múltiples Vistas")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Ajustar el tamaño de la ventana al tamaño de la pantalla
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.cap = None  # Inicializa self.cap aquí
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.picam2 = None 
        self.set_background("fondo.jpg")
        self.show_main()
    def set_background(self, image_path):
        """
        Configura un fondo para el frame principal.
        """
        image = Image.open(image_path)
      
        image.resize((self.root.winfo_width(), self.root.winfo_height()))
        self.frame_background = ImageTk.PhotoImage(image)
        bg_label = tk.Label(self.root, image=self.frame_background)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)


    
    def acceder(self):
        # Directorio con las imágenes
        
        image_folder = os.path.join(self.script_dir, "fotos")
        self.known_face_encodings = {}
        self.reconocimiento = {}
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
        
        # print("Codificaciones cargadas con éxito:", list(self.known_face_encodings.keys()))
    
        self.clear_frame()
        tk.Label(self.root, text="Acceder a tus Medicamentos", font=('Helvetica', 16)).pack(pady=20)
        # self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)  # Inicia la captura de la cámara web
        # self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
        self.picam2.start()
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=20)
        self.update_video()  # Inicia la actualización del video en la GUI
         
        tk.Button(self.root, text="Regresar", command=self.show_main, height=2, width=50).pack(pady=20)

    def update_video(self):
        frame_counter = 0
        if self.picam2:
            frame = self.picam2.capture_array()
            if frame is not None:
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
                                    known_name=known_name.split("_")[0]
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
                            if name!="Desconocido":
                                if known_name not in self.reconocimiento:
                                    self.reconocimiento[known_name] = 0
                                else:
                                    self.reconocimiento[known_name] += 1
                
              
                    cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv_img)

                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                    for clave, valor in self.reconocimiento.items():
                        if valor == 10:
                            tk.messagebox.showinfo("Éxito", f"Usuario : {clave} ha sido reconocido.")
                            self.user=clave
                            self.Resumen()
                       


            self.video_label.after(10, self.update_video)  # Llama a la misma función después de 10 ms
                

    def administar(self):
        self.clear_frame()
        tk.Label(self.root, text="Administar Usuarios", font=('Helvetica', 16)).pack(pady=20)
        tk.Button(self.root, text="Crear Usuario", command=self.agregar_usuario, height=2, width=50).pack(pady=10)
        tk.Button(self.root, text="Eliminar Usuarios", command=self.eliminar_usuario, height=2, width=50).pack(pady=10)
        tk.Button(self.root, text="Administar Medicamentos", command=self.administar_medicamento, height=2, width=50).pack(pady=10)
        tk.Button(self.root, text="Regresar", command=self.show_main, height=2, width=50).pack(pady=20)

    
    def Resumen(self):
        def obtener_turno(hora_actual):
            """
            Determina el turno basado en la hora actual.
            Mañana: 1 AM - 12 PM
            Tarde: 12 PM - 6 PM
            Noche: 6 PM - 24 PM
            """
            if hora_actual >= 1 and hora_actual < 12:
                return 'Mañana'
            elif hora_actual >= 12 and hora_actual < 18:
                return 'Tarde'
            elif hora_actual >= 18 and hora_actual < 24:
                return 'Noche'
            else:
                return 'Fuera de horario'
        self.clear_frame()
        tk.Label(self.root, text="Resumen", font=('Helvetica', 16)).pack(pady=20)

        usuario_seleccionado = self.user
        engine = create_engine(f"sqlite:///{os.path.join(self.script_dir, 'dataBase.db')}") # Cambia por la ruta de tu base de datos
        Session = sessionmaker(bind=engine)
        session = Session()
        usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()

        if usuario and usuario.medicamentos:
            medicamentos = [med.medicamento for med in usuario.medicamentos]
            turnos = [med.horario for med in usuario.medicamentos]
            medicamentos_y_turnos = list(zip(medicamentos, turnos))
            orden_turnos = {'Mañana': 0, 'Tarde': 1, 'Noche': 2}
            # Ordena la lista por el turno usando el diccionario de orden
            medicamentos_y_turnos.sort(key=lambda x: orden_turnos.get(x[1], 3))  # Si no se encuentra el turno, asigna un valor alto

            # Crear un Listbox para mostrar los medicamentos y turnos
            listbox = tk.Listbox(self.root, font=('Helvetica', 12), height=10, width=50)
            listbox.pack(pady=10)
            # Insertar los elementos ordenados en el Listbox
            for med, turno in medicamentos_y_turnos:
                listbox.insert(tk.END, f"Medicamento: {med} - Hora: {turno}")
            # Crear una lista para los medicamentos según el turno actual
            medicamentos_por_turno = {'Mañana': [], 'Tarde': [], 'Noche': []}

            # Obtener la hora actual
            hora_actual = datetime.now().hour
            
            # Asignar medicamentos al turno correspondiente
            for med, turno in zip(medicamentos, turnos):
                turno_actual = obtener_turno(hora_actual)
                if turno == turno_actual:
                    medicamentos_por_turno[turno_actual].append(med)
            self.lista_accion=medicamentos_por_turno[turno_actual]


            
            # Limpiar el estado de los pines GPIO antes de iniciar
            GPIO.cleanup()

            # Configura el modo de numeraciÃ³n de pines
            GPIO.setmode(GPIO.BCM)

            # Configura el pin GPIO donde estÃ¡ conectado el servo
            servo_pin = 17
            GPIO.setup(servo_pin, GPIO.OUT)


            # Configura la seÃ±al PWM en el pin del servo
            pwm = GPIO.PWM(servo_pin, 50)  # 50Hz, frecuencia estÃ¡ndar para servos
            pwm.start(0)  # Inicia con el pulso en 0%

            servo_pin_2= 18
            GPIO.setup(servo_pin_2, GPIO.OUT)


            # Configura la seÃ±al PWM en el pin del servo
            pwm_2 = GPIO.PWM(servo_pin_2, 50)  # 50Hz, frecuencia estÃ¡ndar para servos
            pwm_2.start(0)  # Inicia con el pulso en 0%


            rutas={
                "A":11.2,
                "B":9.8,
                "C":8.1,
                "D":6.4,
                "E":4.7,
}
            for tipo in self.lista_accion:
                pwm_2.ChangeDutyCycle(12.5)   
                time.sleep(1.5)
                pwm.ChangeDutyCycle(2.4)   
                time.sleep(1.5)
                if tipo =="A":
                    pwm_2.ChangeDutyCycle(11 )  
                    time.sleep(1.5)
                    pwm_2.ChangeDutyCycle(rutas[tipo])  
                else:
                    pwm_2.ChangeDutyCycle(rutas[tipo])   
                time.sleep(1.5)
                pwm.ChangeDutyCycle(3.9)   
                time.sleep(1.5)
                pwm.ChangeDutyCycle(9.5)   
                time.sleep(1.5)

             
            # Mostrar en un Label los medicamentos correspondientes al turno actual
            tk.Label(self.root, text=f"Medicamentos para el turno de {obtener_turno(hora_actual)}:", font=('Helvetica', 12)).pack(pady=10)
            
            for turno, meds in medicamentos_por_turno.items():
                if meds:  # Si hay medicamentos para ese turno
                    tk.Label(self.root, text=f"{turno}: {', '.join(meds)}", font=('Helvetica', 12)).pack(pady=5)

        session.close()

        tk.Button(self.root, text="Regresar", command=self.regenerar, height=2, width=50).pack(pady=20)

 
#-----------------------------------------------------------------------------------------------
    def agregar_usuario(self):
        self.clear_frame()
       
        # Campo de texto para ingresar el nombre del usuario
        tk.Label(self.root, text="Escribir aquí el nombre del usuario:", font=('Helvetica', 12)).pack(pady=10)
        name_entry = tk.Entry(self.root, font=('Helvetica', 12), width=30)
        name_entry.pack(pady=10)
        # Sección de cámara
        # self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
        self.picam2.start()
        video_label = tk.Label(self.root)
        video_label.pack(pady=10)

        capture_label = tk.Label(self.root, text="Fotos capturadas: 0/5", font=('Helvetica', 10))
        capture_label.pack(pady=5)

        def update_camera_photo():
            if self.picam2:
                frame = self.picam2.capture_array()
                if frame is not None:
                    frame = cv2.flip(frame, 1)

                    # Dimensiones del recuadro amarillo con forma alargada
                    h, w, _ = frame.shape
                    box_width = w // 3  # Ancho del rectángulo (1/3 del ancho del frame)
                    box_height = h // 2  # Alto del rectángulo (1/2 del alto del frame)
                    box_start = (w // 2 - box_width // 2, h // 2 - box_height // 2)
                    box_end = (w // 2 + box_width // 2, h // 2 + box_height // 2)

                    # Dibujar recuadro amarillo con líneas punteadas
                    color = (0, 255, 255)  # Amarillo
                    thickness = 2
                    line_type = cv2.LINE_AA
                    gap = 15  # Tamaño de la línea punteada

                    # Líneas horizontales
                    for x in range(box_start[0], box_end[0], gap):
                        cv2.line(frame, (x, box_start[1]), (x + gap // 2, box_start[1]), color, thickness, line_type)
                        cv2.line(frame, (x, box_end[1]), (x + gap // 2, box_end[1]), color, thickness, line_type)

                    # Líneas verticales
                    for y in range(box_start[1], box_end[1], gap):
                        cv2.line(frame, (box_start[0], y), (box_start[0], y + gap // 2), color, thickness, line_type)
                        cv2.line(frame, (box_end[0], y), (box_end[0], y + gap // 2), color, thickness, line_type)

                    # Convertir frame para Tkinter
                    cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv_img)
                    imgtk = ImageTk.PhotoImage(image=img)
                    video_label.imgtk = imgtk
                    video_label.configure(image=imgtk)
                video_label.after(10, update_camera_photo)

        def capture_photo():
            if self.picam2:
                frame = self.picam2.capture_array()
                num_photos = 5 # Número de fotos a capturar
                captured = 0

                def take_next_photo():
                    nonlocal captured
                    if captured < num_photos:
                        if self.picam2:
                            frame = self.picam2.capture_array()
                   
                            user_name = name_entry.get().strip()
                            if not user_name:
                                tk.messagebox.showerror("Error", "Por favor, escribe el nombre del usuario.")
                                return
                            # save_path = os.path.join(self.script_dir, "fotos", f"{user_name}")
                            # # Guardar la foto con el nombre ingresado
                            # if not os.path.exists(save_path):
                            #     # Crear la carpeta
                            #     os.makedirs(save_path)
                            save_path = os.path.join(self.script_dir, "fotos",  f"{user_name}_{captured + 1}.jpg")
                        
                            
                            cv2.imwrite(save_path, frame)
                            captured += 1
                            capture_label.config(text=f"Fotos capturadas: {captured}/{num_photos}")
                            if captured >= num_photos:
                           
                                save_path = os.path.join(self.script_dir, "fotos", f"{user_name}",  f"{user_name}_{1}.jpg")
                                engine = create_engine(f"sqlite:///{os.path.join(self.script_dir, 'dataBase.db')}")  # Cambia por la ruta de tu base de datos
                                Session = sessionmaker(bind=engine)
                                session = Session()
                                nuevo_usuario = Usuario(
                                    user=user_name,  # Reemplaza con el nombre del usuario
                                    foto=save_path  # Reemplaza con la ruta de la foto
                                )

                                # Agregar a la sesión y confirmar los cambios
                                session.add(nuevo_usuario)
                                session.commit()
                                
                                tk.messagebox.showinfo("Listo", "Se han tomado todas las fotos.")
                            # Llamar de nuevo a la función después de 1 segundo
                            video_label.after(1000, take_next_photo)
                        else:
                            tk.messagebox.showerror("Error", "No se pudo capturar la foto.")
                  
               
                take_next_photo()

        # Botón para iniciar la captura de fotos
        add_button = tk.Button(self.root, text="Agregar Usuario", font=('Helvetica', 12), height=2, width=50, command=capture_photo)
        add_button.pack(pady=20)
        tk.Button(self.root, text="Regresar", command=self.regenerar, font=('Helvetica', 12), height=2, width=50).pack(pady=20)
        # Iniciar la actualización de la cámara
        update_camera_photo()
    def regenerar(self):
        # Destruir la ventana actual
        self.root.destroy()

        # Volver a crear la ventana
        root = tk.Tk()
        app = App(root)
        root.mainloop()

#-----------------------------------------------------------------------------------------------
    def eliminar_usuario(self):
        self.clear_frame()
        tk.Label(self.root, text="Eliminar Usuarios", font=('Helvetica', 16)).pack(pady=20)

        # Crear una conexión con la base de datos
        engine = create_engine(f"sqlite:///{os.path.join(self.script_dir, 'dataBase.db')}")  # Cambia por tu ruta de base de datos
        Session = sessionmaker(bind=engine)
        session = Session()

        # Obtener la lista de usuarios
        usuarios = session.query(Usuario).all()
        session.close()

        # Combobox para seleccionar usuario
        tk.Label(self.root, text="Selecciona un Usuario para Eliminar").pack(pady=5)
        self.combo_usuarios = ttk.Combobox(self.root, state="readonly", values=[usuario.user for usuario in usuarios])
        self.combo_usuarios.pack(pady=10)

        # Función para eliminar el usuario seleccionado
        def confirmar_eliminar_usuario():
            usuario_seleccionado = self.combo_usuarios.get()

            if usuario_seleccionado:
                # Confirmación de eliminación
                respuesta = tk.messagebox.askyesno(
                    "Confirmar Eliminación",
                    f"¿Estás seguro de que deseas eliminar al usuario '{usuario_seleccionado}' y todos sus medicamentos?"
                )
                if respuesta:
                    session = Session()
                    usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()

                    if usuario:
                        # Eliminar medicamentos asociados
                        medicamentos = session.query(Medicamento).filter_by(user_id=usuario.id).all()
                        for med in medicamentos:
                            session.delete(med)

                        # Eliminar foto del usuario
                        if usuario.foto:
                             
                            try:
                   

                                for archivo in os.listdir(os.path.join(self.script_dir, "fotos")):
                                    if archivo.startswith(usuario.user):
                                        archivo_path = os.path.join(os.path.join(self.script_dir, "fotos"), archivo)
                                        # Eliminar el archivo
                                        if os.path.isfile(archivo_path):
                                            os.remove(archivo_path)
                            except FileNotFoundError:
                                tk.messagebox.showwarning("Advertencia", "No se encontró la foto para eliminar.")

                        # Eliminar usuario
                        session.delete(usuario)
                        session.commit()
                        session.close()

                        tk.messagebox.showinfo("Éxito", f"Usuario '{usuario_seleccionado}' eliminado correctamente.")

                        # Actualizar el Combobox
                        self.combo_usuarios['values'] = [
                            usuario.user for usuario in session.query(Usuario).all()
                        ]
                        self.combo_usuarios.set("")  # Limpiar la selección
                    else:
                        tk.messagebox.showerror("Error", "No se encontró el usuario seleccionado.")
            else:
                tk.messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario.")

        # Botón para eliminar
        tk.Button(self.root, text="Eliminar Usuario", command=confirmar_eliminar_usuario, height=2, width=50).pack(pady=10)

        # Botón para regresar
        tk.Button(self.root, text="Regresar", command=self.administar, height=2, width=50).pack(pady=20)

        
    
    def administar_medicamento(self):
        self.clear_frame()
        tk.Label(self.root, text="Administrar Medicamentos", font=('Helvetica', 16)).pack(pady=20)

        # Combobox para seleccionar usuario
        tk.Label(self.root, text="Selecciona un Usuario").pack(pady=5)
        engine = create_engine(f"sqlite:///{os.path.join(self.script_dir, 'dataBase.db')}")  # Cambia por la ruta de tu base de datos
        Session = sessionmaker(bind=engine)
        session = Session()
        usuarios = session.query(Usuario).all()
        session.close()

        # Frame para contener los combos y listas
        frame_combos = tk.Frame(self.root)
        frame_combos.pack(pady=10)

        # Combobox para usuarios
        self.combo_usuarios = ttk.Combobox(frame_combos, state="readonly", values=[usuario.user for usuario in usuarios])
        self.combo_usuarios.pack(pady=5)

        # Label y Combobox para medicamentos
        tk.Label(self.root, text="Medicamentos del Usuario Seleccionado").pack(pady=5)
        self.combo_medicamentos = ttk.Combobox(self.root, state="readonly")
        self.combo_medicamentos.pack(pady=5)

        # Combobox para nuevo medicamento y horario
        tk.Label(self.root, text="Selecciona un Nuevo Medicamento").pack(pady=5)
        self.combo_nuevo_medicamento = ttk.Combobox(self.root, state="readonly", values=["A", "B", "C", "D","E"])
        self.combo_nuevo_medicamento.pack(pady=5)

        tk.Label(self.root, text="Selecciona un Horario").pack(pady=5)
        self.combo_horario = ttk.Combobox(self.root, state="readonly", values=["Mañana", "Tarde", "Noche"])
        self.combo_horario.pack(pady=5)

        # Función para listar medicamentos según el usuario seleccionado
        def listar_medicamentos(event):
            usuario_seleccionado = self.combo_usuarios.get()
            if usuario_seleccionado:
                session = Session()
                usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()
                if usuario and usuario.medicamentos:
                    medicamentos = [med.medicamento for med in usuario.medicamentos]
                    self.combo_medicamentos.config(values=medicamentos)
                else:
                    self.combo_medicamentos.config(values=[])  # Si no hay medicamentos
                session.close()

        self.combo_usuarios.bind("<<ComboboxSelected>>", listar_medicamentos)

        # Función para agregar un medicamento
        def agregar_medicamento():
            usuario_seleccionado = self.combo_usuarios.get()
            nuevo_medicamento = self.combo_nuevo_medicamento.get()
            horario = self.combo_horario.get()

            if usuario_seleccionado and nuevo_medicamento and horario:
                session = Session()
                usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()
                nuevo_med = Medicamento(medicamento=nuevo_medicamento, horario=horario, usuario=usuario)
                session.add(nuevo_med)
                session.commit()
                listar_medicamentos(None)  # Actualizar la lista de medicamentos
                session.close()
                tk.messagebox.showinfo("Éxito", "Medicamento agregado correctamente.")
            else:
                tk.messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario, medicamento y horario.")

        # Función para editar un medicamento
        def editar_medicamento():
            usuario_seleccionado = self.combo_usuarios.get()
            medicamento_seleccionado = self.combo_medicamentos.get()
            nuevo_medicamento = self.combo_nuevo_medicamento.get()
            nuevo_horario = self.combo_horario.get()

            if usuario_seleccionado and medicamento_seleccionado and nuevo_medicamento and nuevo_horario:
                session = Session()
                usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()
                medicamento = session.query(Medicamento).filter_by(
                    usuario=usuario, medicamento=medicamento_seleccionado
                ).first()
                if medicamento:
                    medicamento.medicamento = nuevo_medicamento
                    medicamento.horario = nuevo_horario
                    session.commit()
                    listar_medicamentos(None)  # Actualizar la lista de medicamentos
                    session.close()
                    tk.messagebox.showinfo("Éxito", "Medicamento editado correctamente.")
                else:
                    tk.messagebox.showerror("Error", "No se encontró el medicamento seleccionado.")
            else:
                tk.messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

        # Función para eliminar un medicamento
        def eliminar_medicamento():
            usuario_seleccionado = self.combo_usuarios.get()
            medicamento_seleccionado = self.combo_medicamentos.get()

            if usuario_seleccionado and medicamento_seleccionado:
                session = Session()
                usuario = session.query(Usuario).filter_by(user=usuario_seleccionado).first()
                medicamento = session.query(Medicamento).filter_by(
                    usuario=usuario, medicamento=medicamento_seleccionado
                ).first()
                if medicamento:
                    session.delete(medicamento)
                    session.commit()
                    listar_medicamentos(None)  # Actualizar la lista de medicamentos
                    session.close()
                    tk.messagebox.showinfo("Éxito", "Medicamento eliminado correctamente.")
                else:
                    tk.messagebox.showerror("Error", "No se encontró el medicamento seleccionado.")
            else:
                tk.messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario y un medicamento.")

        # Botones para acciones
        tk.Button(self.root, text="Agregar Medicamento", command=agregar_medicamento, height=2, width=50).pack(pady=5)
        tk.Button(self.root, text="Editar Medicamento", command=editar_medicamento, height=2, width=50).pack(pady=5)
        tk.Button(self.root, text="Eliminar Medicamento", command=eliminar_medicamento, height=2, width=50).pack(pady=5)
        tk.Button(self.root, text="Regresar", command=self.administar, height=2, width=50).pack(pady=20)


    def show_main(self):
        if self.cap and self.cap.isOpened():  # Asegúrate de liberar la cámara solo si está abierta
            self.cap.release()  # Libera la cámara web cuando regresas al menú principal
        self.clear_frame()
        tk.Label(self.root, text="Bienvenido a PILBOT !", font=('Helvetica', 16)).pack(pady=20)
        tk.Button(self.root, text="Acceder", command=self.acceder, height=3, width=50).pack(pady=20)
        tk.Button(self.root, text="Administar", command=self.administar, height=3, width=50).pack(pady=20)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background("fondo.jpg")  # Restablece el fondo después de limpiar los widgets


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
