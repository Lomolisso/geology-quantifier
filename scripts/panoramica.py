import cv2
import numpy as np
import pyvista as pv
import api_fm

# Variables globales
refPt = []
refPt_array = np.zeros((4,2), dtype='float')
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
    return np.array([a, b, c, d], dtype="float")


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cont,out
    # if the left mouse button was clicked, record the (x, y) 
    if event == cv2.EVENT_LBUTTONDOWN and cont <4:
        # Al hacer click se crea un punto rojo y se guarda
        # el punto seleccionado, sumando 1 al contador de puntos.
        cv2.circle(img, (x,y),5,(0,0,255),-1)
        refPt.append((x, y))
        refPt_array[cont] = [x, y]
        cont+=1 
        if len(refPt) > 1:
            # Si ya hemos seleccionado más de un punto,
            # estos se irán uniendo con lineas para visualizar
            # el rectángulos que se va armando.
            cv2.line(img, refPt[cont-2], refPt[cont-1], (0,0,255), 2)
        if cont == 4:
            # Cuando se llega a 4 ptos se dibuja la última linea
            # y se ordenan los puntos tal que el rectángulo se 
            # pueda cortar y quedar derecho, es decir quedan ordenados
            # en sentido antihorario y el primer punto es de más arriba a 
            # la izquierda.
            cv2.line(img, refPt[0], refPt[cont-1], (0,0,255), 2)
            print(refPt)
            refPt = order_points(refPt_array)
            print(refPt)
            
            # Se calculan las dimensiones del rectángulo
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
            # Se contruye la persepectiva y se corta sobre un clon de la imagen original.
            M = cv2.getPerspectiveTransform(input_pts,output_pts)
            out = cv2.warpPerspective(clone,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)

# Cargamos la imagen, ajustando sus dimenciones para que se pueda
# visualizar completa en la pantalla. 
img = api_fm.load_image()
img = cv2.resize(img, (int(img.shape[1]*0.2),int(img.shape[0]*0.2)))
clone = img.copy()
out = img.copy()
# Creamos una nueva ventana donde se carga la función de mouse creada anteriormente.
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)
# keep looping until the 'x' key is pressed
while True:
    # display the image and wait for a keypress
    cv2.imshow("image", img)
    key = cv2.waitKey(1) & 0xFF
    # Si se preciona 'r' se vuelve a empezar de cero la selcción de puntos.
    if key == ord("r"):
        cont = 0
        refPt = []
        img = clone.copy()
    # if the 'x' key is pressed, break from the loop
    elif key == ord("x"):
        break
# if there are two reference points, then crop the region of interest
# from teh image and display it
if len(refPt) == 4:
	cv2.imshow("Image cut", out)
	cv2.waitKey(0)
# close all open windows
cv2.destroyAllWindows()

# ajustamos la imagen recien cortada para colocarla sobre el tubo
out = cv2.flip(out, 1)
outRGB = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
tex = pv.numpy_to_texture(outRGB)
# Creamos el tubo y luego cargamos sobre él la textura, para
# luego visualizarlo
surf = pv.read('.\scripts\\tubo.obj')
surf.plot(texture=tex, background="black")
