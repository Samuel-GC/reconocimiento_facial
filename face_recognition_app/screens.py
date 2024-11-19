# face_recognition_app/screens.py

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


class SelectableLabel(Label):
    is_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SelectableLabel, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(is_selected=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_selected:
                Color(0, 0.5, 0.5, 0.3)  # Highlight color when selected
            else:
                Color(0, 0, 0, 0)  # No highlight when not selected
            Rectangle(pos=self.pos, size=self.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Clear all other selections
            for sibling in self.parent.children:
                if isinstance(sibling, SelectableLabel):
                    sibling.is_selected = False
            self.is_selected = True  # Select this label
            return True
        return super(SelectableLabel, self).on_touch_down(touch)


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
            if self.is_adding_person:
                frame_with_box = self.face_recognizer.draw_center_box(frame)
                texture = self.camera.convert_frame_to_texture(frame_with_box)
                if texture:
                    self.camera_view.texture = texture
            else:
                annotated_frame = self.face_recognizer.recognize_faces_in_frame(
                    frame, self.data_manager.embeddings, self.data_manager.names
                )
                texture = self.camera.convert_frame_to_texture(annotated_frame)
                if texture:
                    self.camera_view.texture = texture

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


    def assign_medication(self):
        print("assign_medication called")
        if not self.selected_user:
            self.status_label.text = "Por favor, seleccione un usuario."
            return
        medication_info = self.medication_input.text.strip()
        if not medication_info:
            self.status_label.text = "Por favor, ingrese información del medicamento."
            return
        self.med_manager.assign_medication(self.selected_user, medication_info)
        self.status_label.text = f"Medicamento asignado a {self.selected_user}."

    def delete_user(self):
        print("delete_user called")
        if not self.selected_user:
            self.status_label.text = "Por favor, seleccione un usuario para eliminar."
            return

        user_to_delete = self.selected_user
        print(f"Attempting to delete user: {user_to_delete}")

        # Call DataManager to delete the user
        self.data_manager.delete_user(user_to_delete)
        self.status_label.text = f"Usuario eliminado: {user_to_delete}."

        # Clear the selection and refresh the user list
        self.selected_user = None
        self.load_users()