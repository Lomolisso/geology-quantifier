import cv2
import numpy as np
import sys
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
file_name = input("enter the name of the image file: ")
# file_name = 'Litologia-_Areniscas..jpg'

img = cv2.imread(file_name)
img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
cv2.imshow('image', img)

blanck = np.zeros(img.shape, dtype = 'uint8')


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray,(3,3), cv2.BORDER_DEFAULT)
# cannyB = cv2.Canny(1blur, 125, 175)
canny = cv2.Canny(blur, 80, 175)

lines = cv2.HoughLinesP(canny, 1, np.pi/180, 60, np.array([]), 50, 5)

xmin,ymin,xmax, ymax = maxCoords(lines)

img_cut = img[ymin:ymax,xmin:xmax]
# print(lines)
cv2.imshow("lines in image1", img_cut)
gray1 = cv2.cvtColor(img_cut, cv2.COLOR_BGR2GRAY)
blur1 = cv2.GaussianBlur(gray1,(3,3), cv2.BORDER_DEFAULT)
canny1 = cv2.Canny(blur1, 80, 150)
cv2.imshow('canny2', canny1)

lines1 = cv2.HoughLinesP(canny1, 1, np.pi/180, 60, np.array([]), 50, 5)
xmin1,ymin1,xmax1, ymax1 = maxCoords(lines1)
img_cut1 = img_cut[ymin1:ymax1,xmin1:xmax1]

img = img_cut1
# img = cv2.imread('images/Litologia-Riolitas_Tobas_Aglomerado_Volcanico.jpg')
img = cv2.resize(img, (int(1296),int(1823)))
img = cv2.resize(img, (int(img.shape[1]*0.3),int(img.shape[0]*0.3)))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(gray,50,200)
canny = cv2.dilate(canny,None,iterations=1)
cv2.imshow('gray',canny)
cv2.waitKey(0)
cv2.destroyAllWindows()
#cv2.imshow('gray',thresh)
contours, hierarchy = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
print ('hierarchy=',hierarchy)
img_area = img.shape[1] * img.shape[0]
rect_list = []
for c in contours:
    rect = cv2.boundingRect(c)
    x,y,w,h = rect
    area = w*h
    if area< img_area*0.5 and area > img_area*0.20:
        
        a = (rect[0]+50,rect[1]+50,rect[2]-100,rect[3]+10)
        print(rect)
        #area = cv2.minAreaRect(rect)
        #cv2.drawContours(img , [c], -1, (0,0,255), 3)
        cv2.rectangle(img , rect, (0,0,255), 1)
        rect_list.append(rect)

cv2.imshow('imagen',img)
mask = np.zeros(img.shape[:2], dtype="uint8")
rect_mask = cv2.rectangle(mask,rect_list[0], 255, -1)
masked = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow('masked image', masked)
cv2.waitKey(0)
cv2.destroyAllWindows()
#"""
"""
import cv2
import numpy as np
url = 'images/Litologia-_Granito.jpg'
img = cv2.imread(url)
img = cv2.resize(img, (int(img.shape[1]*0.4),int(img.shape[0]*0.4)))
mask = np.zeros(img.shape[:2],np.uint8)
bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)
rect = (0,0,img.shape[0],img.shape[1])
blur = cv2.blur(img, (7,7))
cv2.grabCut(blur,mask,rect,bgdModel,fgdModel,1,cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
contornos,_ = cv2.findContours(mask2, cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
for c in contornos:
    nvCont = cv2.convexHull(c)
    cv2.drawContours(img, [nvCont], -1, (255,0,0), 3)


cv2.imshow('frame',img)
#img = img*mask2[:,:,np.newaxis]
#cv.imshow('nombre',img)"""
