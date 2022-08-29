"""import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN

img = cv2.imread('a-50.png')

Z = np.float32(img.reshape((-1,3)))
db = DBSCAN(eps=0.3, min_samples=10).fit(Z[:,:2])

plt.imshow(np.uint8(db.labels_.reshape(img.shape[:2])))
plt.show()
#cv2.waitKey(0)
#cv2.destroyAllWindows()"""
import cv2
import matplotlib.pyplot as plt
import numpy as np

from skimage.filters import threshold_otsu

img = cv2.imread('geology-quantifier/b4.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
Z = np.float32(img.reshape((-1,3)))

img = cv2.pyrMeanShiftFiltering(img, 20, 10, 3)
img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

plt.imshow(img)
plt.show()

imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
print ('hierarchy=',hierarchy)
cv2.drawContours(img , contours, -1, (0,0,255), 3)
cv2.imshow('imagen',img)
cv2.imshow('thresh', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
"""
img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
img_gray=cv2.cvtColor(img_rgb,cv2.COLOR_RGB2GRAY)

def filter_image(image, mask):
    r = image[:,:,0] * mask
    g = image[:,:,1] * mask
    b = image[:,:,2] * mask
    return np.dstack([r,g,b])

thresh = threshold_otsu(img_gray)
img_otsu  = img_gray < thresh
filtered = filter_image(img, img_otsu)
cv2.imshow('imagen',filtered)
cv2.waitKey(0)
cv2.destroyAllWindows()"""

