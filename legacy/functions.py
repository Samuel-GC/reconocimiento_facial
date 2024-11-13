import cv2
from mtcnn import MTCNN
data_dir = './imagenes'

def getImgFromCascade(img, img_res=64):
    # Cargar los clasificadores de rostros (frontal y perfil)
    face_cascade_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros frontales
    faces = face_cascade_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Si no hay rostros frontales, buscar perfiles
    if len(faces) == 0:
        faces = face_cascade_profile.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Procesar el primer rostro detectado
    if len(faces) > 0:
        (x, y, w, h) = faces[0]  # Solo el primer rostro detectado
        face_roi = img[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (img_res, img_res))  # Redimensionar a 64x64
        # images.append(face_roi)
        # labels.append(label_dict[folder])
        return face_roi,(x, y, w, h)
    
    return None, None

detector = MTCNN()

def getImgFromMTCNN(img, img_res=64):
    # Inicializar el detector de rostros

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertir a RGB para MTCNN

    # Detectar rostros en la imagen
    faces = detector.detect_faces(img_rgb)
    
    # Procesar el primer rostro detectado (o todos si deseas entrenar con varios rostros por imagen)
    if faces:
        x, y, width, height = faces[0]['box']  # Solo el primer rostro detectado
        face_roi = img[y:y+height, x:x+width]
        face_roi = cv2.resize(face_roi, (img_res, img_res))  # Redimensionar a 64x64
        return face_roi,(x, y, width, height)
    
    return None, None



def getImgFromPRE(img, img_res=64):
# Ruta de los archivos del modelo de detección de rostros
    modelFile = "opencv_face_detector_uint8.pb"  # Asegúrate de que esté en la misma carpeta o especifica la ruta completa
    configFile = "opencv_face_detector.pbtxt"    # Asegúrate de que esté en la misma carpeta o especifica la ruta completa
    net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)

    # Preparar la imagen para la red de detección de rostros
    h, w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    
    # Procesar detecciones
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Ajustar el umbral según sea necesario
            x1 = int(detections[0, 0, i, 3] * w)
            y1 = int(detections[0, 0, i, 4] * h)
            x2 = int(detections[0, 0, i, 5] * w)
            y2 = int(detections[0, 0, i, 6] * h)

            # Recortar el rostro detectado
            face_roi = img[y1:y2, x1:x2]

            face_roi = cv2.resize(face_roi, (img_res, img_res))  # Redimensionar a 64x64

            return face_roi, (x1, y1, x2, y2)

    return None, None