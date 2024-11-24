# face_recognition_app/medication_manager.py

import json
import os
from datetime import datetime

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

    def assign_medication(self, name, medication_info, schedule):
        if name not in self.medications:
            self.medications[name] = []
        self.medications[name].append({
            'medication': medication_info,
            'schedule': schedule  # Lista de horarios en formato 'HH:MM'
        })
        self.save_medications()

    def get_medications(self, name):
        return self.medications.get(name, [])

    def delete_medication(self, name, medication_info):
        if name in self.medications:
            self.medications[name] = [
                m for m in self.medications[name] if m['medication'] != medication_info
            ]
            if not self.medications[name]:
                del self.medications[name]
            self.save_medications()

    def check_medication_time(self, name):
        current_time = datetime.now().strftime('%H:%M')
        medications_due = []
        for med in self.get_medications(name):
            if current_time in med['schedule']:
                medications_due.append(med['medication'])
        return medications_due
