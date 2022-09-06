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
import api_fm
import sampleExtraction

def run_histogram_equalization(rgb_img):
    # convert from RGB color-space to YCrCb
    ycrcb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YCrCb)

    # equalize the histogram of the Y channel
    ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])

    # convert back to RGB color-space from YCrCb
    return cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2BGR)

def contornoMeanshift(org_img):
    img = run_histogram_equalization(org_img)
    cv2.imshow('equalized_img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    Z = np.float32(img.reshape((-1,3)))

    #img = cv2.pyrMeanShiftFiltering(img, 50, 5, 3)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

def gen_masks(mask_num):
    output_masks = []
    # Get image from file
    img = sampleExtraction.extract_sample()

    # Kmeans stuff
    twoDimage = img.reshape((-1,3))
    twoDimage = np.float32(twoDimage)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    attempts=10
    _,label,_=cv2.kmeans(twoDimage,mask_num,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

    label = label.flatten()
    for cluster in range(0,mask_num):
        # convert to the shape of a vector of pixel values
        masked_image = np.copy(img)

        # color (i.e cluster) to disable
        masked_image = masked_image.reshape((-1, 3))
        masked_image[label != cluster] = [0, 0, 0]

        # convert back to original shape
        masked_image = masked_image.reshape(img.shape)

        # append mask to output
        output_masks.append(masked_image)

    return output_masks

#img = cv2.pyrMeanShiftFiltering(img, 50, 5, 3)
#img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

#plt.imshow(img)
#plt.show()


# img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
# for K in range(2,10):
#     im = np.copy(img)
#     twoDimage = img.reshape((-1,3))
#     twoDimage = np.float32(twoDimage)
#     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
#     attempts=10
#     ret,label,center=cv2.kmeans(twoDimage,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)
#     # ret,label,center=cv2.kmeans(twoDimage,K,None,criteria,attempts,cv2.KMEANS_RANDOM_CENTERS)
#     center = np.uint8(center)
    
#     res = center[label.flatten()]
#     result_image = res.reshape((img.shape))
#     #cv2.imshow('imagen',result_image)
#     #cv2.waitKey(0)
#     #cv2.destroyAllWindows()
    
#     label = label.flatten()
#     for cluster in range(0,K):
#         masked_image = np.copy(im)
#         # convert to the shape of a vector of pixel values
#         masked_image = masked_image.reshape((-1, 3))


#         # color (i.e cluster) to disable
        
#         masked_image[label != cluster] = [0, 0, 0]

#         # convert back to original shape
#         masked_image = masked_image.reshape(im.shape)
#         # show the image
#         cv2.imshow(f'{cluster}',masked_image)
#         # api_fm.save_image(cluster)
#         api_fm.save_image_as(cluster)
    
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
    #plt.imshow(img)
    #plt.show()


#img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
# K = 3
# im = np.copy(img)
# twoDimage = img.reshape((-1,3))
# twoDimage = np.float32(twoDimage)
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
# attempts=10
# ret,label,center=cv2.kmeans(twoDimage,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)
# center = np.uint8(center)

# res = center[label.flatten()]
# result_image = res.reshape((img.shape))
# #cv2.imshow('imagen',result_image)
# #cv2.waitKey(0)
# #cv2.destroyAllWindows()

# label = label.flatten()
# for cluster in range(0,K):
#     masked_image = np.copy(im)
#     # convert to the shape of a vector of pixel values
#     masked_image = masked_image.reshape((-1, 3))
#     # color (i.e cluster) to disable
    
#     masked_image[label != cluster] = [0, 0, 0]

#     # convert back to original shape
#     masked_image = masked_image.reshape(im.shape)
#     # show the image
#     cv2.imshow(f'{cluster}',masked_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

"""
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
print ('hierarchy=',hierarchy)
cv2.drawContours(img , contours, -1, (0,0,255), 3)
cv2.imshow('imagen',img)
cv2.imshow('thresh', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
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
