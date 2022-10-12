"""
Shape detection implementation for
the geology-cuantifier project.
"""

import cv2, numpy as np
import percent

COLORS = [(255,0,0), (0,255,0), (0,0,255)]


class ContourData(object):
    """
    This class is in charge of holding
    relevant data of a contour, such as 
    It's bounding rectangle and a mask
    with only the pixels in that region.
    """

    def __init__(self, img, r) -> None:
        """
        Class constructor, instantiates class
        params. such as the bounding rect. of a contour
        and It's mask.
        """
        self.img = img
        self.r = r

    def aspect_ratio(self) -> float:
        """
        When called, this function returns
        the aspect ratio of the bounding rect
        of the contour.
        """
        _, _, w, h = self.r
        return w/h

def contour_segmentation(img):
    """
    Finds the contours of the image, for each computes
    It's bounding rect and mask. Then draws the contours 
    and returns a list with all the data.
    """
    data = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (_, threshInv) = cv2.threshold(gray, 1, 255,cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(threshInv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        mask = np.zeros(img.shape[:2], dtype="uint8")
        r = cv2.boundingRect(cnt)
        cv2.drawContours(mask, [cnt],-1, (255,255,255),-1)
        masked = cv2.bitwise_and(img,img, mask = mask)
        x,y,w,h = r
        masked = masked[y:y+h, x:x+w]
        data.append(ContourData(masked,r))
    return data

def contour_agrupation(contours):
    """
    Runs a basic agrupation by comparing the aspect ratio
    of each contour's bounding rect.
    """
    for c in contours:
        asp_rat = c.aspect_ratio()
        if asp_rat <= 1.2 and asp_rat >= 0.8:
            # Square like rectangles
            c.group = 0
        elif asp_rat <= 1.5 and asp_rat >= 0.5:
            c.group = 1
        else:
            c.group = 2

def cluster_segmentation(cluster, contours):
    """
    Once each CountourData instance is successfully 
    agrupated, this function draws each bounding rect.
    
    The rectangle colour will be given by the group of the 
    ContourData instance.
    """
    im = np.copy(cluster)
    for c in contours:
        color = COLORS[c.group]
        cv2.rectangle(im, c.r, color, 2)
    return im

def generate_results(contours):
    """
    Calculate statistics for each group.
    """
    total_percentages = [0,0,0]
    prom_percentages = [0,0,0]
    num_of_contors = [0,0,0]
    for c in contours:
        per = percent.percent(c.img)
        total_percentages[c.group] += per
        num_of_contors[c.group] += 1
    for i in range(3):
        if num_of_contors[i] != 0:
            prom_percentages[i] = total_percentages[i]/num_of_contors[i]
    return total_percentages, prom_percentages