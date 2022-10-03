import cv2, numpy as np
import percent

class Contour():
    def __init__(self, img, r) -> None:
        self.img = img
        self.r = r

    def aspect_ratio(self):
        _,_,w,h = self.r
        return w/h


def contour_segmentation(img):
    masks = []
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
        masks.append(Contour(masked,r))
    return masks

 

def contour_agrupation(contours):
    for c in contours:
        asp_rat = c.aspect_ratio()
        if asp_rat > 1.2:
            c.group = 0
        elif asp_rat < 0.8:
            c.group = 1
        else:
            c.group = 2

COLORS = [(255,0,0), (0,255,0), (0,0,255)]
def cluster_segmentation(cluster, contours):
    im = np.copy(cluster)
    for c in contours:
        color = COLORS[c.group]
        cv2.rectangle(im, c.r, color, 2)
    return im

def generate_results(contours):
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