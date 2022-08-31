import cv2
import numpy as np
import imutils
import os

ASPECT_RATIO =16,9
RESOLUTION =1920//4, 1080//4

Datos = 'p'
if not os.path.exists(Datos):
    print('Carpeta creada: ',Datos)
    os.makedirs(Datos)
cap = cv2.VideoCapture(0)
def area(data):
        _, _, w, h = data["rect"]
        return w*h
while True:
    
    ret,frame = cap.read()
    resized_img = cv2.resize(frame, RESOLUTION)
    cv2.imshow("Resized image to standards", resized_img)
    grayscale_image = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    grayscale_image = cv2.blur(grayscale_image,(3,3))

    # Then we detect the edges of the image and enhance them
    canny = cv2.Canny(grayscale_image, 50, 200)
    canny = cv2.dilate(canny, None, iterations=1)
    cv2.imshow('Edges of input (canny + dilate)', canny)
    """
    # We compute the contours of the image in order to detect
    # the biggest rectangle that contains them, i.e. the rock sample.
    contours, _ = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours_data = [{"contour":c, "rect":cv2.boundingRect(c)} for c in contours]

    

    sample_data = max(contours_data, key=area)
    s_contour = sample_data["contour"]
    s_x, s_y, s_w, s_h = sample_data["rect"]
    cvx_hull_contour = cv2.convexHull(s_contour)

    # We cut the resized_sample according to the max area rect.
    detected_sample = resized_img[s_y:s_y+s_h,s_x:s_x+s_w]
    cv2.imshow('Detected rock sample', detected_sample)
    

    # Using the contour of the rock sample we can compute
    # a mask that will allow us to delete te background of the image
    mask = np.zeros_like(resized_img)
    cv2.drawContours(mask, [cvx_hull_contour], -1, (255,255,255), -1)
    mask = mask[s_y:s_y+s_h,s_x:s_x+s_w]

    cv2.imshow('Mask for background deletion', mask)
    

    # We apply the mask and delete the background
    output = np.zeros_like(detected_sample)
    output[(mask > 0)] = detected_sample[(mask > 0)]

    cv2.imshow('Detected rock sample without background', output)
    

    """
    if cv2.waitKey(1) == ord('q'):
        cv2.imwrite("hola.jpg",resized_img)
    
    if cv2.waitKey(1) == 27:
        break
cap.release()
cv2.destroyAllWindows()
