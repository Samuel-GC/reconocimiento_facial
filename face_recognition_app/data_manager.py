# face_recognition_app/data_manager.py

import pickle
import numpy as np
import os

class DataManager:
    def __init__(self, data_dir='data', embedding_size=1280):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.embeddings_file = os.path.join(self.data_dir, 'embeddings.pkl')
        self.names_file = os.path.join(self.data_dir, 'names.pkl')
        self.embedding_size = embedding_size

        # Inicializar las propiedades antes de cargar los datos
        self.embeddings = np.empty((0, self.embedding_size))
        self.names = []

        # Cargar los datos
        self.embeddings, self.names = self.load_data()

    def save_data(self):
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        with open(self.names_file, 'wb') as f:
            pickle.dump(self.names, f)

    def load_data(self):
        if not os.path.exists(self.embeddings_file) or not os.path.exists(self.names_file):
            embeddings = np.empty((0, self.embedding_size))
            names = []
            return embeddings, names

        with open(self.embeddings_file, 'rb') as f:
            embeddings = pickle.load(f)
        with open(self.names_file, 'rb') as f:
            names = pickle.load(f)

        # Verificar y corregir inconsistencias
        if len(embeddings) != len(names):
            print("Inconsistencia detectada: corrigiendo datos...")
            min_length = min(len(embeddings), len(names))
            embeddings = embeddings[:min_length]
            names = names[:min_length]
            self.save_data()

        return embeddings, names
    
    def add_embedding(self, embedding, name):
        self.embeddings = np.vstack([self.embeddings, embedding])
        self.names.append(name)
        self.save_data()

    def delete_user(self, user):
        if user in self.names:
            index = self.names.index(user)
            # Eliminar el nombre y el embedding correspondiente
            self.names.pop(index)
            self.embeddings = np.delete(self.embeddings, index, axis=0)
            self.save_data()  # Guardar los datos actualizados
            print(f"Usuario eliminado: {user}")
        else:
            print("Usuario no encontrado en la lista.")