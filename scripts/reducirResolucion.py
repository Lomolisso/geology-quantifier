import cv2
from api_fm import load_image, save_image

#Porcentaje en el que se redimensiona la imagen
scale_percent = 50
src = load_image()
#calcular el 50 por ciento de las dimensiones originales
width = int(src.shape[1] * scale_percent / 100)
height = int(src.shape[0] * scale_percent / 100)
 
# dsize
dsize = (width, height)
 
# cambiar el tamaño de la image
output = cv2.resize(src, dsize)
 
save_image(output)
