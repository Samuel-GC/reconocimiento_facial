# face_recognition_app/medication_manager.py

import json
import os

class MedicationManager:
    def __init__(self, medication_file='medications/medications.json'):
        os.makedirs(os.path.dirname(medication_file), exist_ok=True)
        self.medication_file = medication_file
        self.medications = self.load_medications()

    def load_medications(self):
        if not os.path.exists(self.medication_file):
            return {}
        with open(self.medication_file, 'r') as f:
            medications = json.load(f)
        return medications

    def save_medications(self):
        with open(self.medication_file, 'w') as f:
            json.dump(self.medications, f, indent=4)

    def assign_medication(self, name, medication_info):
        self.medications[name] = medication_info
        self.save_medications()

    def get_medication(self, name):
        return self.medications.get(name, {})
