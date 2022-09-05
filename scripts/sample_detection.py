"""
This module is in charge of detecting a rock sample
in an image. To do so the script does the following:

    - standarizes the image
    - detects the edges of the image
    - computes the contours of the image
    - find the max area rectangle that contains a contour
    - using that contour, computes a mask for background deletion
    - deletes the background of the image

The script is called in console with: python3 sample_detection.py <filename>
The input of the script must be located at: ../img/raw/<filename>
The output of the script will be located at: ../img/processed/isolated_<filename>

"""

import cv2
import numpy as np
from api_fm import load_image, save_image

# Script standards for testing the detection
ASPECT_RATIO = 9, 16
RESOLUTION = 1080, 1920


img, img_name = load_image()

# First we resize the input to the standards.
resized_img = cv2.resize(img, RESOLUTION)
cv2.imshow("Resized image to standards", resized_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# We transform to grayscale and apply a blur
grayscale_image = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
grayscale_image = cv2.blur(grayscale_image,(3,3))

# Then we detect the edges of the image and enhance them
canny = cv2.Canny(grayscale_image, 50, 200)
canny = cv2.dilate(canny, None, iterations=1)
cv2.imshow('Edges of input (canny + dilate)', canny)
cv2.waitKey(0)
cv2.destroyAllWindows()

# We compute the contours of the image in order to detect
# the biggest rectangle that contains them, i.e. the rock sample.
contours, _ = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
contours_data = [{"contour":c, "rect":cv2.boundingRect(c)} for c in contours]

def area(data):
    _, _, w, h = data["rect"]
    return w*h

sample_data = max(contours_data, key=area)
s_contour = sample_data["contour"]
s_x, s_y, s_w, s_h = sample_data["rect"]
cvx_hull_contour = cv2.convexHull(s_contour)

# We cut the resized_sample according to the max area rect.
detected_sample = resized_img[s_y:s_y+s_h,s_x:s_x+s_w]
cv2.imshow('Detected rock sample', detected_sample)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Using the contour of the rock sample we can compute
# a mask that will allow us to delete te background of the image
mask = np.zeros_like(resized_img)
cv2.drawContours(mask, [cvx_hull_contour], -1, (255,255,255), -1)
mask = mask[s_y:s_y+s_h,s_x:s_x+s_w]

cv2.imshow('Mask for background deletion', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()

# We apply the mask and delete the background
output = np.zeros_like(detected_sample)
output[(mask > 0)] = detected_sample[(mask > 0)]

cv2.imshow('Detected rock sample without background', output)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Finally we store the output image as a file
save_image(output)