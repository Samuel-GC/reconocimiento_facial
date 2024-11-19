# face_recognition_app/face_recognizer.py

import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras import layers
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity

class FaceRecognizer:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.detector = MTCNN()
        self.embedding_model = self.load_embedding_model()
        self.in_encoder = Normalizer(norm='l2')

    def load_embedding_model(self):
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = layers.GlobalAveragePooling2D()(x)
        model = Model(inputs=base_model.input, outputs=x)
        return model

    def recognize_faces_in_frame(self, frame, embeddings, names):
        faces, coords = self.extract_faces(frame)
        for i, face in enumerate(faces):
            embedding = self.get_embedding(face)
            name, _ = self.recognize_face(embedding, embeddings, names)
            x1, y1, x2, y2 = coords[i]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if not name:
                name = 'Desconocido'
            cv2.putText(frame, name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        return frame

    def extract_faces(self, frame):
        faces = []
        coords_list = []
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

    def draw_center_box(self, frame):
        h, w, _ = frame.shape
        box_size = int(min(w, h) * 0.5)
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return frame

    def extract_face_from_center_box(self, frame):
        h, w, _ = frame.shape
        box_size = int(min(w, h) * 0.5)
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size
        face = frame[y1:y2, x1:x2]
        if face.size == 0:
            return None
        face = cv2.resize(face, (224, 224))
        return face
