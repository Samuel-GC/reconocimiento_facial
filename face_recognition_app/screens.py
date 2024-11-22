# face_recognition_app/screens.py

import dlib
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
import threading
import cv2

from face_recognition_app.camera_module import CameraModule
from face_recognition_app.face_recognizer import FaceRecognizer
from face_recognition_app.data_manager import DataManager
from face_recognition_app.medication_manager import MedicationManager

# Set this variable to True to use the Raspberry Pi Camera, or False for a USB/Laptop camera
use_pi_camera = False  # Change to False if using a USB or laptop camera
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            self.parent.select_with_touch(self.index, touch)
            return True
        return False

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            print(f"Seleccionado: {rv.data[index]['text']}")
        else:
            print(f"Des-seleccionado: {rv.data[index]['text']}")

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

# Register the SelectableLabel class with Kivy's Factory
Factory.register('SelectableLabel', cls=SelectableLabel)

class MainMenu(Screen):
    camera_view = ObjectProperty(None)
    name_input = ObjectProperty(None)
    instructions_label = ObjectProperty(None)
    status_label = ObjectProperty(None)
    add_person_fields = ObjectProperty(None)
    is_adding_person = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
                # Pass the use_pi_camera variable when initializing CameraModule
        self.camera = CameraModule(use_pi_camera=use_pi_camera)
        self.face_recognizer = FaceRecognizer()
        self.data_manager = DataManager()
        self.update_event = None
        self.captured_embeddings = []
        self.num_images_to_capture = 5

    def on_enter(self):
        print("MainMenu on_enter called")
        self.camera.start()
        self.update_event = Clock.schedule_interval(self.update_frame, 1.0 / 30)

    def on_leave(self):
        print("MainMenu on_leave called")
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None
        self.camera.stop()

    def show_add_person_fields(self):
        print("show_add_person_fields called")
        self.is_adding_person = True

    def hide_add_person_fields(self):
        print("hide_add_person_fields called")
        self.is_adding_person = False
        self.name_input.text = ''
        self.status_label.text = ''

    def update_frame(self, dt):
        frame = self.camera.get_frame()
        if frame is not None:
            # Si se está agregando una nueva persona, mostrar el cuadro amarillo y verificar rostro
            if self.is_adding_person:
                # Dimensiones de la imagen
                h, w, _ = frame.shape
                box_size = int(min(w, h) * 0.5)

                # Coordenadas del cuadro amarillo punteado
                x1 = (w - box_size) // 2
                y1 = (h - box_size) // 2
                x2 = x1 + box_size
                y2 = y1 + box_size

                # Dibujar cuadro amarillo punteado
                self.draw_dotted_rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

                # Mostrar mensaje de instrucciones
                cv2.putText(frame, "Acerque el rostro hasta que este dentro del recuadro",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # Detectar rostros
                faces, coords = self.face_recognizer.extract_faces(frame)
                if coords:
                    # Usar el primer rostro detectado
                    x_face1, y_face1, x_face2, y_face2 = coords[0]

                    # Comprobar si el rostro está dentro del cuadro amarillo
                    if x1 < x_face1 < x2 and x1 < x_face2 < x2 and y1 < y_face1 < y2 and y1 < y_face2 < y2:
                        color = (0, 255, 0)  # Verde: rostro dentro del cuadro
                        self.is_face_inside_box = True
                    else:
                        color = (0, 0, 255)  # Rojo: rostro fuera del cuadro
                        self.is_face_inside_box = False
                        cv2.putText(frame, "Por favor, centre el rostro en el recuadro",
                                    (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    # Dibujar el cuadro alrededor del rostro
                    cv2.rectangle(frame, (x_face1, y_face1), (x_face2, y_face2), color, 2)

            # Convertir el marco a textura y mostrarlo
            texture = self.camera.convert_frame_to_texture(frame)
            if texture:
                self.camera_view.texture = texture


# Función para dibujar un cuadro punteado
    def draw_dotted_rectangle(self, img, pt1, pt2, color, thickness, gap=10):
        x1, y1 = pt1
        x2, y2 = pt2
        for x in range(x1, x2, gap):
            cv2.line(img, (x, y1), (x + gap // 2, y1), color, thickness)
            cv2.line(img, (x, y2), (x + gap // 2, y2), color, thickness)
        for y in range(y1, y2, gap):
            cv2.line(img, (x1, y), (x1, y + gap // 2), color, thickness)
            cv2.line(img, (x2, y), (x2, y + gap // 2), color, thickness)

    def start_capture(self):
        print("start_capture called")
        if not self.is_adding_person:
            return

        name = self.name_input.text.strip()
        if not name:
            self.status_label.text = "Por favor, ingrese un nombre válido."
            return

        self.status_label.text = "Capturando imágenes..."
        self.captured_embeddings = []
        captures = 0

        while captures < self.num_images_to_capture:
            frame = self.camera.get_frame()
            if frame is not None:
                face = self.face_recognizer.extract_face_from_center_box(frame)
                if face is not None:
                    embedding = self.face_recognizer.get_embedding(face)
                    self.captured_embeddings.append(embedding)
                    captures += 1
                    self.status_label.text = f"Imágenes capturadas: {captures}/{self.num_images_to_capture}"
                    cv2.waitKey(500)  # Wait 500 ms between captures
                else:
                    self.status_label.text = "No se detectó rostro. Intente nuevamente."
                    cv2.waitKey(500)
            else:
                self.status_label.text = "No se pudo capturar el frame. Intente nuevamente."
                cv2.waitKey(500)

        if self.captured_embeddings:
            avg_embedding = sum(self.captured_embeddings) / len(self.captured_embeddings)
            self.data_manager.add_embedding(avg_embedding, name)
            self.status_label.text = f"{name} ha sido registrado exitosamente."
            self.hide_add_person_fields()

class SettingsScreen(Screen):
    user_list = ObjectProperty(None)
    medication_input = ObjectProperty(None)
    status_label = ObjectProperty(None)
    selected_user = None  # Correctly define the single selected user

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.med_manager = MedicationManager()
        self.data_manager = DataManager()

    def on_enter(self):
        print("SettingsScreen on_enter called")
        threading.Thread(target=self.load_users).start()

    def load_users(self):
        print("Loading users...")
        # Ensure that users are plain strings
        users = set(self.data_manager.names)
        self.user_list.data = [{'text': str(name)} for name in users]  # Make sure these are strings
        print(self.user_list.data)
        Clock.schedule_once(lambda dt: self.user_list.refresh_from_data(), 0)


    def on_user_select(self, user_text):
        self.selected_user = str(user_text)  # Directly set as a string
        print(f"Selected user: {self.selected_user}")  # Debugging output


    def get_selected_user(self):
        selected_nodes = self.user_list.layout_manager.selected_nodes
        if selected_nodes:
            index = selected_nodes[0]
            selected_user = self.user_list.data[index]['text']
            return selected_user
        else:
            return None
    
    def delete_user(self):
        print("delete_user called")
        selected_user = self.get_selected_user()
        if not selected_user:
            self.status_label.text = "Por favor, seleccione un usuario para eliminar."
            return

        print(f"Attempting to delete user: {selected_user}")

        # Llamar a DataManager para eliminar el usuario
        self.data_manager.delete_user(selected_user)
        self.status_label.text = f"Usuario eliminado: {selected_user}."

        # Actualizar la lista de usuarios
        self.load_users()

    def assign_medication(self):
        print("assign_medication called")
        selected_user = self.get_selected_user()
        if not selected_user:
            self.status_label.text = "Por favor, seleccione un usuario."
            return
        medication_info = self.medication_input.text.strip()
        if not medication_info:
            self.status_label.text = "Por favor, ingrese información del medicamento."
            return
        self.med_manager.assign_medication(selected_user, medication_info)
        self.status_label.text = f"Medicamento asignado a {selected_user}."
