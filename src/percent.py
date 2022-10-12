"""
Script to detect the percent of pixels that aren't black in an image.
You need to call percent(img) passing the target image to count
it's non black pixels.
"""

import cv2
import numpy as np

BLACK = [0, 0, 0]
DIFF = 0
SCALE_RATIO = 1

def percent(image):
    """
    Calculates the percentage of colored pixels in a 
    given image. 
    """
    
    # detection interval, note that it is on BGR.
    lower, upper = (
        np.array([BLACK[2]-DIFF, BLACK[1]-DIFF, BLACK[0]-DIFF], dtype=np.uint8),
        np.array([BLACK[2]+DIFF, BLACK[1]+DIFF, BLACK[0]+DIFF], dtype=np.uint8)
    )

    # calculate the new dimensions
    s_width, s_height = int(image.shape[1] * SCALE_RATIO), int(image.shape[0] * SCALE_RATIO)

    # resize the image:
    img = cv2.resize(image, (s_width, s_height), None, None, None, cv2.INTER_AREA)

    # apply binarization of the image using the interval (lower, upper)
    mask = cv2.inRange(img, lower, upper)   # 3 channel img

    # calculate the ratio of black pixels in mask
    black_pixels_ratio = cv2.countNonZero(mask) / (img.size/3)

    # calculate the color percent
    black_percent = (black_pixels_ratio * 100) / SCALE_RATIO
    color_percent = 100 - black_percent
    return np.round(color_percent, 2)
