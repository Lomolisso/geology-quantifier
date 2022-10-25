import numpy as np
import cv2
import percent as pc
import random
import image_managers
from tkinter import filedialog

def img_with_percent(img, percent):
    shape_x,shape_y = img.shape[0], img.shape[1]
    area = shape_x*shape_y
    pixels_to_print = area*percent/100
    while(pixels_to_print>0):
        pixelx = random.randint(0, shape_x-1)
        pixely = random.randint(0, shape_y-1)
        if((img[pixelx,pixely]==0).any()):
            img[pixelx,pixely]=[255,255,255]
            pixels_to_print-=1

def chessboardPattern(img,vertical,horizontal):
    shape_x,shape_y = img.shape[0], img.shape[1]
    for i in range(0,vertical):
        for j in range(i%2,horizontal,2):
            cv2.rectangle(img, ( j*shape_y//horizontal,i*shape_x//vertical),((j+1)*shape_y//horizontal-1,(i+1)*shape_x//vertical-1), (255,255,255),-1)



height = 400
width =400
channels = 3
img = np.zeros((height,width,channels), dtype=np.uint8)
#chessboardPattern(img,8,3)
img_with_percent(img,80)
cv2.circle(img,(200,200), 20, [255,255,0], -1)
perc_calc = pc.percent(img)



print("Porcentaje de blanco calculado: " + str(perc_calc))
cv2.imshow("blank_image", img)
cv2.imwrite("img_test.png",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
