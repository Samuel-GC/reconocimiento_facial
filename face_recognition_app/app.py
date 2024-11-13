# face_recognition_app/app.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
import os

from face_recognition_app.screens import MainMenu, AddPersonScreen, SettingsScreen

class FaceRecognitionApp(App):
    def build(self):
        # Load the Kivy GUI layout
        kv_file = os.path.join(os.path.dirname(__file__), 'kivy_gui.kv')
        Builder.load_file(kv_file)

        # Create the screen manager and add screens
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(AddPersonScreen(name='add_person'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm
