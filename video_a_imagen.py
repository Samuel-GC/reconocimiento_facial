import cv2
import os

# Ruta del video
video_path = 'D:/escritorio/reconocimiento_facial/videos/samuel/video_1.mp4'
# Ruta de la carpeta donde se guardarán las imágenes
folder_path = 'D:/escritorio/reconocimiento_facial/imagenes/samuel'
# Crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Cargar el video
cap = cv2.VideoCapture(video_path)

# Inicializar el contador de imágenes
count = 0

# Leer el video cuadro por cuadro
while True:
    success, frame = cap.read()
    if not success:
        break  # Si no hay más cuadros, salir del bucle

    # Guardar el cuadro como una imagen
    cv2.imwrite(f"{folder_path}/frame_{count:04d}.png", frame)
    count += 1

# Liberar el objeto capturador de video
cap.release()

print(f"Video segmentado en {count} imágenes guardadas en '{folder_path}'")
