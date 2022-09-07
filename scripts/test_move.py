import cv2 as cv
import math

#Este archivo hace la función de elegir los puntos de una imagen panorámica para que otra función externa
#tenga dichos puntos y así recortarla como un rectángulo, hay que reemplazar la elección de puntos original
#por este código. Al presionar algún botón para elegir el momento en el que se tienen los puntos deseados
#(a definir) se deben utilizar los puntos guardados hasta ese momento y proseguir con el resto del proceso


def rescale(frame, scale = 0.2):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    #print(dimensions)
    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)

#dibuja circulos con las lineas que las unen en el orden conveniente
def draw_circles_and_lines(frame, r, c1, c2, c3, c4):
    cv.circle(frame, c1, r, RED, -1) 
    cv.circle(frame, c2, r, RED, -1) 
    cv.circle(frame, c3, r, RED, -1) 
    cv.circle(frame, c4, r, RED, -1)
    cv.line(frame, c1, c2, BLUE)
    cv.line(frame, c2, c4, BLUE)
    cv.line(frame, c3, c4, BLUE)
    cv.line(frame, c3, c1, BLUE) 

#fórmula pitagórica para calcular diferencia entre el punto del click y el de algún otro punto
def dif_circle(center, x, y):
    dif_x = abs(x - center[0])
    dif_y = abs(y - center[1])
    return math.sqrt(dif_x**2 + dif_y**2)





def mouse(event,x,y, flags, params):
    global move_circle_1, move_circle_2, move_circle_3, move_circle_4, BLUE, bg
    global r1_center, r2_center, r3_center, r4_center, bg_size
    if event == cv.EVENT_LBUTTONDOWN:
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
    elif event == cv.EVENT_MOUSEMOVE and x <= bg_size[1] and y <= bg_size[0] and x >= 0 and y>=0:
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
    elif event == cv.EVENT_LBUTTONUP:
        bg = bg_original.copy()
        draw_circles_and_lines(bg, radius, r1_center, r2_center, r3_center, r4_center)
        move_circle_1 = False
        move_circle_2 = False
        move_circle_3 = False
        move_circle_4 = False

if __name__ == '__main__':

    

    move_circle_1 = False
    move_circle_2 = False
    move_circle_3 = False
    move_circle_4 = False
    BLUE = [255,0,0]
    RED = [0, 0, 255]
    GREEN = [0, 255, 0]

    #bg es la imagen, basta con cambiar la URL a la imagen deseada

    #Apliqué un rescale a la imagen, eso se puede modificar

    bg = rescale(cv.imread('./img/raw/DIO_1_Panoramica.jpg'))

    bg_original = bg.copy()

    bg_size = bg.shape

    #radio de los puntos visibles en la imagen
    radius = 7

    #Estos son los 4 puntos (en orden son A, B, C y D), son variables globales
    #En teoría siempre son A, B, C y D en ese orden, a menos que alguien deforme el cuadrilátero visible
    #(o lo invierta), estos casos son mejorables pero lo haré a futuro (para impedir que un punto cruze
    # una línea)
    #Tienen valores iniciales equivalentes a las 4 esquinas de la imagen y se van modificando con el código,
    #si están muy esquinadas inicialmente se pueden correr algunos píxeles hacia adentro en la pos. inicial

    r1_center = (0,0)
    r2_center = (0,bg_size[0])
    r3_center = (bg_size[1],0)
    r4_center = (bg_size[1],bg_size[0])

    draw_circles_and_lines(bg, radius, r1_center, r2_center, r3_center, r4_center)

    cv.namedWindow('draw')
    cv.setMouseCallback('draw', mouse)

    #Por ahora, para matar al código hay que apretar Esc (si se aprieta la X se vuelve a poner la imagen,
    # y por razones desconocidas no se mueven los círculos, pero en teoría no se debería hacer eso XD, 
    # error a arreglar a futuro)

    while True:

        cv.imshow('draw', bg)
        k = cv.waitKey(1)

        #waiting for esc to exit
        if k == 27 & 0xFF:
            break

    cv.destroyAllWindows()