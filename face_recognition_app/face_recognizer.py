import cv2
import numpy as np
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Importar modelos de detección facial
from mtcnn.mtcnn import MTCNN  # Importa MTCNN
import dlib  # Importa Dlib

class FaceRecognizer:
    def __init__(self, model_type='dlib', threshold=0.5):
        self.threshold = threshold
        self.model_type = model_type.lower()
        self.in_encoder = Normalizer(norm='l2')

        # Inicializar el detector de rostros basado en el modelo seleccionado
        if self.model_type == 'mtcnn':
            self.detector = MTCNN()
        elif self.model_type == 'dlib':
            if not os.path.exists("shape_predictor_68_face_lanasdmarks.dat"):
                print("El archivo no se encuentra en la ruta especificada.")
            self.detector = dlib.get_frontal_face_detector()
            # self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Ruta al modelo de puntos
        else:
            raise ValueError("Modelo de detección no soportado. Usa 'mtcnn' o 'dlib'.")

        # Cargar el modelo de embeddings (puede que desees usar un modelo más ligero en un Raspberry Pi)
        self.embedding_model = self.load_embedding_model()

    def load_embedding_model(self):
        # Aquí puedes considerar un modelo más ligero si lo ejecutas en un Raspberry Pi
        from tensorflow.keras.applications import MobileNetV2  # MobileNetV2 es más rápido y ligero
        from tensorflow.keras.models import Model
        from tensorflow.keras import layers

        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = layers.GlobalAveragePooling2D()(x)
        model = Model(inputs=base_model.input, outputs=x)
        return model
    
    def draw_center_box(self, frame):
        h, w, _ = frame.shape
        box_size = int(min(w, h) * 0.5)
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return frame
    
    def recognize_faces_in_frame(self, frame, embeddings, names):
        faces, coords = self.extract_faces(frame)
        for i, face in enumerate(faces):
            embedding = self.get_embedding(face)
            name, similarity = self.recognize_face(embedding, embeddings, names)
            x1, y1, x2, y2 = coords[i]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if not name:
                name = 'Desconocido'
            # Mostrar nombre y nivel de similitud
            text = f"{name} ({similarity*100:.2f}%)"
            cv2.putText(frame, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        return frame

    def extract_faces(self, frame):
        faces = []
        coords_list = []

        if self.model_type == 'mtcnn':
            results = self.detector.detect_faces(frame)
            for result in results:
                x1, y1, width, height = result['box']
                x1, y1 = abs(x1), abs(y1)
                x2, y2 = x1 + width, y1 + height
                face = frame[y1:y2, x1:x2]
                if face.size == 0:
                    continue
                face = cv2.resize(face, (224, 224))
                faces.append(face)
                coords_list.append((x1, y1, x2, y2))
        elif self.model_type == 'dlib':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_dlib = self.detector(gray)
            for rect in faces_dlib:
                x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
                face = frame[y1:y2, x1:x2]
                if face.size == 0:
                    continue
                face = cv2.resize(face, (224, 224))
                faces.append(face)
                coords_list.append((x1, y1, x2, y2))
                 # Dibujar los 68 puntos faciales
                # landmarks = self.predictor(gray, rect)
                # for n in range(0, 68):
                #     x = landmarks.part(n).x
                #     y = landmarks.part(n).y
                #     cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # Dibujar cada punto con un círculo verde


        return faces, coords_list

    def get_embedding(self, face):
        face = face.astype('float32') / 255.0
        face = np.expand_dims(face, axis=0)
        embedding = self.embedding_model.predict(face, verbose=0)
        return embedding[0]

    def recognize_face(self, face_embedding, embeddings, names):
        if len(embeddings) == 0:
            return 'Desconocido', 0.0
        face_embedding_norm = self.in_encoder.transform(face_embedding.reshape(1, -1))
        embeddings_norm = self.in_encoder.transform(embeddings)
        similarities = cosine_similarity(face_embedding_norm, embeddings_norm)
        max_similarity = np.max(similarities)
        index = np.argmax(similarities)
        if max_similarity > self.threshold:
            name = names[index]
        else:
            name = 'Desconocido'
        return name, max_similarity

    def extract_face_from_center_box(self, frame):
        h, w, _ = frame.shape
        box_size = int(min(w, h) * 0.5)
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size

        if self.model_type == 'mtcnn':
            results = self.detector.detect_faces(frame)
            for result in results:
                x, y, width, height = result['box']
                x2_face, y2_face = x + width, y + height

                if x1 < x < x2 and x1 < x2_face < x2 and y1 < y < y2 and y1 < y2_face < y2:
                    face = frame[y:y+height, x:x+width]
                    if face.size == 0:
                        continue
                    face = cv2.resize(face, (224, 224))
                    return face
        elif self.model_type == 'dlib':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_dlib = self.detector(gray)
            for rect in faces_dlib:
                x = rect.left()
                y = rect.top()
                x2_face = rect.right()
                y2_face = rect.bottom()

                if x1 < x < x2 and x1 < x2_face < x2 and y1 < y < y2 and y1 < y2_face < y2:
                    face = frame[y:y2_face, x:x2_face]
                    if face.size == 0:
                        continue
                    face = cv2.resize(face, (224, 224))
                    return face
        return None