import cv2
import numpy as np

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

def gen_masks(img, cluster_num):
    # List of the output masks
    output_masks = []

    # Kmeans stuff
    twoDimage = img.reshape((-1,3))
    twoDimage = np.float32(twoDimage)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    attempts=10
    _,label,_=cv2.kmeans(twoDimage,cluster_num,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

    label = label.flatten()
    for cluster in range(0,cluster_num):
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
