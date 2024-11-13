import cv2
import os

segmentos=20

count = 0
count_video=0
user="samuel"
video_path = f'D:/escritorio/reconocimiento_facial/videos/{user}/'
folder_path = f'D:/escritorio/reconocimiento_facial/imagenes/{user}'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

for video in os.listdir(video_path):
    count_video=0
 
    count_segmentos= 0

    # Cargar el video
    cap = cv2.VideoCapture(video_path+video)

    # Inicializar el contador de imágenes


    # Leer el video cuadro por cuadro
    while True:
        success, frame = cap.read()
        if not success:
            break  # Si no hay más cuadros, salir del bucle
        if count_segmentos ==segmentos:

            # Guardar el cuadro como una imagen
            cv2.imwrite(f"{folder_path}/img_{count:04d}.png", frame)
            count += 1
            count_video+=1
            count_segmentos= 0 
        else:
            count_segmentos +=1

    # Liberar el objeto capturador de video
    cap.release()

    print(f"Video {video} , segmentado en {count_video} imágenes  ")
