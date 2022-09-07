"""
Script to manualy cut the target sample of an image.
You can do it calling extract_sample(img) passing the 
image you want to cut.
"""
import cv2
import numpy as np
import math

TOKEN = "[EXTRACT]"

def draw_circles_and_lines(frame, r, c1, c2, c3, c4):
    cv2.circle(frame, c1, r, RED, -1) 
    cv2.circle(frame, c2, r, RED, -1) 
    cv2.circle(frame, c3, r, RED, -1) 
    cv2.circle(frame, c4, r, RED, -1)
    cv2.line(frame, c1, c2, BLUE)
    cv2.line(frame, c2, c4, BLUE)
    cv2.line(frame, c3, c4, BLUE)
    cv2.line(frame, c3, c1, BLUE) 

# Pythagorean formula for calculating the difference between 
# the click point and some other point.
def dif_circle(center, x, y):
    dif_x = abs(x - center[0])
    dif_y = abs(y - center[1])
    return math.sqrt(dif_x**2 + dif_y**2)

def mouse(event,x,y, flags, params):
    global move_circle_1, move_circle_2, move_circle_3, move_circle_4, BLUE, bg
    global r1_center, r2_center, r3_center, r4_center, bg_size
    if event == cv2.EVENT_LBUTTONDOWN:
        dif_1 = dif_circle(r1_center, x, y)
        dif_2 = dif_circle(r2_center, x, y)
        dif_3 = dif_circle(r3_center, x, y)
        dif_4 = dif_circle(r4_center, x, y)
        if dif_1 <= radius:
            move_circle_1 = True
        elif dif_2 <= radius:
            move_circle_2 = True        
        elif dif_3 <= radius:
            move_circle_3 = True        
        elif dif_4 <= radius:
            move_circle_4 = True
    elif event == cv2.EVENT_MOUSEMOVE and x <= bg_size[1] and y <= bg_size[0] and x >= 0 and y>=0:
        bg = bg_original.copy() 
        if move_circle_1:
            r1_center = (x, y)
        elif move_circle_2:
            r2_center = (x, y)
        elif move_circle_3:
            r3_center = (x, y)
        elif move_circle_4:
            r4_center = (x, y)
        draw_circles_and_lines(bg, radius, r1_center, r2_center, r3_center, r4_center)
    elif event == cv2.EVENT_LBUTTONUP:
        bg = bg_original.copy()
        draw_circles_and_lines(bg, radius, r1_center, r2_center, r3_center, r4_center)
        move_circle_1 = False
        move_circle_2 = False
        move_circle_3 = False
        move_circle_4 = False

def extract_sample(img):
    global RED, BLUE, GREEN, move_circle_1, move_circle_2, move_circle_3, move_circle_4
    global radius, bg, bg_original, bg_size, r1_center, r2_center, r3_center, r4_center
    move_circle_1 = False
    move_circle_2 = False
    move_circle_3 = False
    move_circle_4 = False
    BLUE = [255,0,0]
    RED = [0, 0, 255]
    GREEN = [0, 255, 0]

    img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
    bg = img

    bg_original = bg.copy()

    bg_size = bg.shape

    # radius of the visible points in the image
    radius = 7

    # The points r1,r2,r4,r3 _center are the corners of the rectangle, the are
    # global vars and it must be in these order (1,2,4,3).
    # TODO prevent the inversion of the point order.
    # Initially the 4 points are in the center of the image.

    r1_center = (bg_size[1]//4, bg_size[0]//4)
    r2_center = (bg_size[1]//4, bg_size[0]*3//4)
    r4_center = (bg_size[1]*3//4, bg_size[0]*3//4)
    r3_center = (bg_size[1]*3//4, bg_size[0]//4)

    draw_circles_and_lines(bg, radius, r1_center, r2_center, r3_center, r4_center)    

    cv2.namedWindow('draw')
    cv2.setMouseCallback('draw', mouse)
    print(f"{TOKEN} Use 's' to save or 'r' to reset the cut, 'Esc' for exit.")
    
    while True:
        
        cv2.imshow('draw', bg)
        k = cv2.waitKey(1)

        # if 'Esc' is pressed, the cuting stops.
        if k == 27 & 0xFF:
            cv2.destroyAllWindows()
            return

        # if 's' is pressed, the img was cut in the rectangle area.
        elif k == ord("s"):
            refPt = [r1_center, r2_center, r4_center, r3_center]

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
            # The perspective is built and cut on a clone of the original image.
            M = cv2.getPerspectiveTransform(input_pts,output_pts)
            out = cv2.warpPerspective(bg_original,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
            cv2.imshow("Image cut", out)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return out

        # if 'r' is pressed, the rectangle return to the original position.
        elif k == ord('r'):
            r1_center = (0,0)
            r2_center = (0,bg_size[0])
            r4_center = (bg_size[1],bg_size[0])
            r3_center = (bg_size[1],0)