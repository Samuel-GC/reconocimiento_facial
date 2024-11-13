import cv2
import numpy as np

# Ruta de los archivos del modelo de detección de rostros
modelFile = "opencv_face_detector_uint8.pb"  # Asegúrate de que esté en la misma carpeta o especifica la ruta completa
configFile = "opencv_face_detector.pbtxt"    # Asegúrate de que esté en la misma carpeta o especifica la ruta completa
net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)

{"model":model, "label_dict":label_dict_inverted}

def testing(parameters):
    
    # Iniciar la captura de video
    cap = cv2.VideoCapture(0)  # 0 es la cámara por defecto

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Preparar la imagen para la detección de rostros
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
        net.setInput(blob)
        detections = net.forward()

        # Procesar las detecciones
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Ajustar el umbral si es necesario
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)

                # Recortar el rostro detectado
                face_roi = frame[y1:y2, x1:x2]

                # Preprocesar el rostro para la predicción
                face_roi_resized = cv2.resize(face_roi, (64, 64))  # Redimensionar a 64x64
                
                face_roi_resized = face_roi_resized / 255.0  # Normalizar
                face_roi_resized = np.expand_dims(face_roi_resized, axis=0)  # Expansión de dimensiones

                # Realizar la predicción
                predictions = model.predict(face_roi_resized)
                class_index = np.argmax(predictions)
                
                # Verificar si class_index está en el diccionario de etiquetas
                if class_index in label_dict_inverted:
                    class_label = label_dict_inverted[class_index]
                    confidence = predictions[0][class_index]

                    # Mostrar la predicción en la imagen
                    text = f"{class_label}: {confidence:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Dibujar un cuadro alrededor del rostro detectado
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Mostrar el cuadro de video con la predicción
        cv2.imshow("Reconocimiento Facial en Tiempo Real", frame)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()