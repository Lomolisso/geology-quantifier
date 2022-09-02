from weakref import ref
import cv2
import numpy as np
import argparse
from matplotlib.cm import get_cmap

import pyvista as pv
from pyvista import examples
import api_fm

refPt = []
refPt_array = np.zeros((4,2), dtype='float')
cropping = False
cont = 0

def pointwise_distance(pts1, pts2):
    """Calculates the distance between pairs of points

    Args:
        pts1 (np.ndarray): array of form [[x1, y1], [x2, y2], ...]
        pts2 (np.ndarray): array of form [[x1, y1], [x2, y2], ...]

    Returns:
        np.array: distances between corresponding points
    """
    dist = np.sqrt(np.sum((pts1 - pts2)**2, axis=1))
    return dist

def order_points(pts):
    """Orders points in form [top left, top right, bottom right, bottom left].
    Source: https://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/

    Args:
        pts (np.ndarray): list of points of form [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    Returns:
        [type]: [description]
    """
    # sort the points based on their x-coordinates
    x_sorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    left_most = x_sorted[:2, :]
    right_most = x_sorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    a, b = left_most

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point. Note: this is a valid assumption because
    # we are dealing with rectangles only.
    # We need to use this instead of just using min/max to handle the case where
    # there are points that have the same x or y value.
    dist = pointwise_distance(np.vstack([a, b]), right_most)
    
    d, c = right_most[np.argsort(dist)[::-1], :]

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([b, a, d, c], dtype="float")


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, cont,out
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN and cont <4:
        cv2.circle(img, (x,y),5,(0,0,255),-1)
        refPt.append((x, y))
        refPt_array[cont] = [x, y]
        cont+=1 
        if len(refPt) > 1:
            cv2.line(img, refPt[cont-2], refPt[cont-1], (0,0,255), 2)
        if cont == 4:
            
            cv2.line(img, refPt[0], refPt[cont-1], (0,0,255), 2)
            print(refPt)
            refPt = order_points(refPt_array)
            print(refPt)
            # Here, I have used L2 norm. You can use L1 also.
            width_AD = np.sqrt(((refPt[0][0] - refPt[3][0]) ** 2) + ((refPt[0][1] - refPt[3][1]) ** 2))
            width_BC = np.sqrt(((refPt[1][0] - refPt[2][0]) ** 2) + ((refPt[1][1] - refPt[2][1]) ** 2))
            maxWidth = max(int(width_AD), int(width_BC))


            height_AB = np.sqrt(((refPt[0][0] - refPt[1][0]) ** 2) + ((refPt[0][1] - refPt[1][1]) ** 2))
            height_CD = np.sqrt(((refPt[2][0] - refPt[3][0]) ** 2) + ((refPt[2][1] - refPt[3][1]) ** 2))
            maxHeight = max(int(height_AB), int(height_CD))

            input_pts = np.float32([refPt[0], refPt[1], refPt[2], refPt[3]])
            output_pts = np.float32([[0, 0],
                                    [0, maxHeight - 1],
                                    [maxWidth - 1, maxHeight - 1],
                                    [maxWidth - 1, 0]])
            # Compute the perspective transform M
            M = cv2.getPerspectiveTransform(input_pts,output_pts)
            out = cv2.warpPerspective(clone,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)

            pass
    # elif event == cv2.EVENT_LBUTTONUP:
    # # record the ending (x, y) coordinates and indicate that
    # # the cropping operation is finished
    #     refPt.append((x, y))
    #     cropping = False
    #     # draw a rectangle around the region of interest
    #     cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)
    #     cv2.imshow("image", img)


img = api_fm.load_image()
img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
cv2.imshow("imagen", img)

# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="Path to the image")
# args = vars(ap.parse_args())
# # load the image, clone it, and setup the mouse callback function
# image = cv2.imread(args["image"])
clone = img.copy()
out = img.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)
# keep looping until the 'q' key is pressed
while True:
    # display the image and wait for a keypress
    cv2.imshow("image", img)
    key = cv2.waitKey(1) & 0xFF
    # if the 'r' key is pressed, reset the cropping region
    if key == ord("r"):
        cont = 0
        refPt = []
        img = clone.copy()
    # if the 'c' key is pressed, break from the loop
    elif key == ord("x"):
        break
# if there are two reference points, then crop the region of interest
# from teh image and display it
if len(refPt) == 4:
	# roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
	cv2.imshow("ROI", out)
	cv2.waitKey(0)
# close all open windows
api_fm.save_image(out)
cv2.waitKey(0)
cv2.destroyAllWindows()

# cv2.destroyAllWindows()

# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# blur = cv2.GaussianBlur(gray,(5,5), cv2.BORDER_DEFAULT)

# sobely = cv2.Sobel(blur,cv2.CV_8UC1,0,1,ksize=5)
# sobely = cv2.dilate(sobely,None,iterations=1)
# cv2.imshow("sobel", sobely)
# # cannyB = cv2.Canny(1blur, 125, 175)
# canny = cv2.Canny(blur, 80, 175)
# contours, hierarchy = cv2.findContours(sobely, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
# # cv2.drawContours(img , contours, -1, (0,0,255), 3)
# img_area = img.shape[1] * img.shape[0]
# for c in contours:
#     rect = cv2.boundingRect(c)
#     x,y,w,h = rect
#     area = w*h
#     if area > img_area*0.5:
#     # print("Área encontrada: ", area)
#         cv2.rectangle(img , rect, (0,0,255), 1)

# cv2.imshow("canny", canny)
# cv2.imshow("imagen con contornos", img)
