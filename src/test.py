import numpy as np
import cv2
import percent as pc
import random
import image_managers
from tkinter import filedialog
from shape_detection import contour_segmentation

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

def test_area():
    height = 400
    width =400
    channels = 3
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea cuadrado
    cv2.rectangle(img, (0,0),(100,100), (255,255,255), -1)
    cv2.rectangle(img, (150,150),(200,200), (255,0,255), -1)
    cv2.rectangle(img, (200,0),(210,10), (255,255,0), -1)
    areas = [100,2500,10000]
    data = contour_segmentation(img)
    for cnt in data:
        print((cnt.get_area() in areas))    
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea rectangulos
    cv2.rectangle(img, (0,0),(140,100), (255,255,255), -1)
    #1.4
    cv2.rectangle(img, (150,150),(250,200), (255,0,255), -1)
    #2 rectangle considera el pixel final como perteneciente a rectangulo a dibujar.
    cv2.rectangle(img, (200,0),(220,10), (255,255,0), -1)
    #2
    areas = [14000,5000,200]
    data = contour_segmentation(img)
    for cnt in data:
        print((cnt.get_area() in areas)) 
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)

    #se testea circulos
    cv2.circle(img, (10,10),10, (255,255,255), -1)
    cv2.circle(img, (150,150),40, (255,0,255), -1)
    cv2.circle(img, (300,50),50, (255,255,0), -1)
    data = contour_segmentation(img)
    areas = 3.14*np.array([10,40,50])*np.array([10,40,50])
    print(areas)
    for cnt in data:
        print(cnt.get_area())
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250],[350,250],[300,350]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    data = contour_segmentation(img)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250], [350,250],[280,200],[300,300],[320,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260], [60,220]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    data = contour_segmentation(img)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def test_aspect_ratio():
    height = 400
    width =400
    channels = 3
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea cuadrado
    cv2.rectangle(img, (0,0),(100,100), (255,255,255), -1)
    cv2.rectangle(img, (150,150),(200,200), (255,0,255), -1)
    cv2.rectangle(img, (200,0),(210,10), (255,255,0), -1)
    data = contour_segmentation(img)
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea rectangulos
    cv2.rectangle(img, (0,0),(140,100), (255,255,255), -1)
    #1.4
    cv2.rectangle(img, (150,150),(249,199), (255,0,255), -1)
    #2 rectangle considera el pixel final como perteneciente a rectangulo a dibujar.
    cv2.rectangle(img, (200,0),(219,9), (255,255,0), -1)
    #2
    data = contour_segmentation(img)
    for cnt in data:
        #TODO asserts
        print(cnt.aspect_ratio())
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)

    #se testea circulos
    cv2.circle(img, (10,10),10, (255,255,255), -1)
    cv2.circle(img, (150,150),40, (255,0,255), -1)
    cv2.circle(img, (300,50),50, (255,255,0), -1)
    data = contour_segmentation(img)
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250],[350,250],[300,350]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    data = contour_segmentation(img)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250], [350,250],[280,200],[300,300],[320,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260], [60,220]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    for cnt in data:
        print(cnt.aspect_ratio() == 1)
    data = contour_segmentation(img)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

test_area()
test_aspect_ratio()


"""
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
cv2.destroyAllWindows() """
