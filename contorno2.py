import cv2

img = cv2.imread('images/jurel.jpg')
img = cv2.resize(img, (int(1296),int(1823)))
img = cv2.resize(img, (int(img.shape[1]*0.3),int(img.shape[0]*0.3)))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.blur(gray,(3,3))
#ret, thresh = cv2.threshold(gray, 127, 255, 0)
canny = cv2.Canny(gray,50,200)
canny = cv2.dilate(canny,None,iterations=1)
cv2.imshow('gray',canny)
cv2.waitKey(0)
cv2.destroyAllWindows()
#cv2.imshow('gray',thresh)
contours, hierarchy = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
print ('hierarchy=',hierarchy)
rect = ()
for c in contours:
    rect = cv2.boundingRect(c)
    x,y,w,h = rect
    area = w*h
    ratio = w/h
    if area>20000 and area < 70000:
        print(ratio)
        a = (rect[0]+50,rect[1]+50,rect[2]-100,rect[3]+10)
        print(rect)
        #area = cv2.minAreaRect(rect)
        #cv2.drawContours(img , [c], -1, (0,0,255), 3)
        img_cut1 = img[y:y+h,x:x+w]
        cv2.imshow('imagen',img_cut1)
        cv2.rectangle(img , rect, (0,0,255), 3)
        
        #cv2.imshow('imagen',img)
        #cv2.waitKey(0)
#cv2.imshow('imagen',img)
#cv2.imshow('thresh', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

"""

#import cv2
import numpy as np
#url = 'images/Litologia-_Granito.jpg'
#img = cv2.imread(url)
#img = cv2.resize(img, (int(img.shape[1]*0.4),int(img.shape[0]*0.4)))
mask = np.zeros(img.shape[:2],np.uint8)
bgdModel = np.zeros((1,65),np.float64)
fgdModel = np.zeros((1,65),np.float64)
blur = cv2.blur(img, (7,7))
cv2.grabCut(blur,mask,rect,bgdModel,fgdModel,1,cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
contornos,_ = cv2.findContours(mask2, cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
for c in contornos:
    nvCont = cv2.convexHull(c)
    cv2.drawContours(img, [nvCont], -1, (255,0,0), 3)

"""


#img = img*mask2[:,:,np.newaxis]
#cv.imshow('nombre',img)"""
