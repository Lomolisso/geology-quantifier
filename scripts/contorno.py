import cv2
import numpy as np
import sys
import api_fm
from matplotlib import pyplot as plt
# import Image

# im1 = Image.open(sys.argv[1])

#maxCoords: list[list[int]] -> int, int, int, int
#Retorna las coordenadar máxima y mínima de una lista de pares (x,y,x,y)

def maxCoords(lines):
    xmin,ymin,xmax, ymax = lines[0][0]
    for line in lines:
        for x1, y1, x2, y2 in line:
            xmi = min(x1,x2)
            ymi = min(y1,y2)
            xma = max(x1,x2)
            yma = max(y1,y2)
            if xmi<xmin:
                xmin = xmi
            if xma>xmax:
                xmax = xma
            if ymi<ymin:
                ymin = ymi
            if yma>ymax:
                ymax = yma
                
    return xmin,ymin,xmax,ymax
#input para leer el archivo
#file_name = api_fm.load_image()
# file_name = 'Litologia-_Areniscas..jpg'

img = api_fm.load_image()
img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
cv2.imshow('image', img)

blanck = np.zeros(img.shape, dtype = 'uint8')


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray,(1,1), cv2.BORDER_DEFAULT)
# cannyB = cv2.Canny(1blur, 125, 175)
canny = cv2.Canny(gray, 80, 175)

lines = cv2.HoughLinesP(canny, 1, np.pi/180, 60, np.array([]), 50, 7)

xmin,ymin,xmax, ymax = maxCoords(lines)

img_cut = img[ymin:ymax,xmin:xmax]
print(xmin,ymin,xmax, ymax)
# cv2.imshow('imc', img_cut)

gray1 = cv2.cvtColor(img_cut, cv2.COLOR_BGR2GRAY)
blur1 = cv2.GaussianBlur(gray1,(3,3), cv2.BORDER_DEFAULT)
canny1 = cv2.Canny(gray1, 80, 150)
# cv2.imshow('canny2', canny1)

lines1 = cv2.HoughLinesP(canny1, 1, np.pi/180, 60, np.array([]), 50,7)
xmin,ymin,xmax, ymax = maxCoords(lines1)

img_cut1 = img_cut[ymin:ymax,xmin:xmax]
# cv2.imshow("lines in image1", img_cut1)
print(xmin,ymin,xmax, ymax)
img = img_cut1
cv2.waitKey(0)
cv2.destroyAllWindows()
# img = cv2.imread('images/Litologia-Riolitas_Tobas_Aglomerado_Volcanico.jpg')
# img = cv2.resize(img, (int(1296),int(1823)))

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(3,3), cv2.BORDER_DEFAULT)
canny = cv2.Canny(blur,30,180)
# canny = cv2.dilate(canny,None,iterations=1)
# cv2.imshow('gray',canny)
#cv2.imshow('gray',thresh)
contours, hierarchy = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
# print ('hierarchy=',hierarchy)
img_area = img.shape[1] * img.shape[0]
rect_list = []
color = (0,0,255)
i = 5
j = 0
k = -10
for c in contours:
    rect = cv2.boundingRect(c)
    x,y,w,h = rect
    area = w*h
    if area< img_area*0.8 and area > img_area*0.15:
        print("Área encontrada: ", area)
        cv2.rectangle(img , rect, (color[0] + i, color[1] + j, color[2] + k), 1)
        rect_list.append(rect)
        i+=100
        j+= 40
        k -=60
        # print(i,j,k)
plt.imshow(img)
cv2.imshow('imagen',img)

mask = np.zeros(img.shape[:2], dtype="uint8")
rect_pos = 0
if len(rect_list) > 1:
    rect_pos = int(input("Elegir contorno más adecuado: "))

rect_mask = cv2.rectangle(mask,rect_list[rect_pos], 255, -1)
print(img.shape[0],img.shape[1])
x,y,w,h = rect_list[rect_pos]
x2 = x+w
y2= y+h
if(x>0):
    x=x-10
    x2 = x2 +10
img2 = img[y:y2, x:x2]
masked = cv2.bitwise_and(img, img, mask=mask)
img = cv2.resize(img, (int(img.shape[1]*1.1),int(img.shape[0]*1.1)))
# cv2.imshow('masked image', masked)

#Aquí van las dimensiones correctas

cv2.imshow('cut masked image', img2)


cv2.waitKey(0)

cv2.destroyAllWindows()
#"""
