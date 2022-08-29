import cv2

#Porcentaje en el que se redimensiona la imagen
scale_percent = 50
src = cv2.imread('../img/raw/b4.png')
#calcular el 50 por ciento de las dimensiones originales
width = int(src.shape[1] * scale_percent / 100)
height = int(src.shape[0] * scale_percent / 100)
 
# dsize
dsize = (width, height)
 
# cambiar el tamaño de la image
output = cv2.resize(src, dsize)
 
cv2.imwrite('../img/processed/b4.png',output)
