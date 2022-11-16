import numpy as np
import cv2
import percent as pc
import random
from shape_detection import contour_segmentation

def img_with_percent(img, percent):
    shape_x,shape_y = img.shape[0], img.shape[1]
    area = shape_x*shape_y
    pixels_to_print = area*percent/100
    while(pixels_to_print>0):
        pixelx = random.randint(0, shape_x-1)
        pixely = random.randint(0, shape_y-1)
        if((img[pixelx,pixely]==0).any()):
            img[pixelx,pixely]=[255,255,255]
            pixels_to_print-=1

def chessboardPattern(img,vertical,horizontal):
    shape_x,shape_y = img.shape[0], img.shape[1]
    for i in range(0,vertical):
        for j in range(i%2,horizontal,2):
            cv2.rectangle(img, ( j*shape_y//horizontal,i*shape_x//vertical),((j+1)*shape_y//horizontal-1,(i+1)*shape_x//vertical-1), (255,255,255),-1)

def math_area(array):
    "calculo del area con determinante, los puntos deben estar ordenados y no crear agujeros en la figura"
    detizq = 0
    detder = 0
    for i in range(len(array)):
        if i ==len(array)-1:
            detizq += array[i][0]*array[0][1]
            detder += array[i][1]*array[0][0]
        else:
            detizq += array[i][0]*array[i+1][1]
            detder += array[i][1]*array[i+1][0]
    if 1/2*(detizq-detder)>0: 
        return 1/2*(detizq-detder)
    else: 
        return -1/2*(detizq-detder)

def math_aspect_ratio(array):
    maxx=max(fila[0] for fila in array)
    print(maxx)
    minx=min(fila[0] for fila in array)
    print(minx)
    maxy=max(fila[1] for fila in array)
    print(maxy)
    miny=min(fila[1] for fila in array)
    print(miny)
    x = maxx-minx+1
    y = maxy-miny+1
    ratio = x/y
    if ratio<1:
        ratio = 1/ratio
    return ratio

def poli_gen(n, center, radius):
    x, y = center
    theta = np.sort(np.random.rand(n))
    theta = 2*np.pi*theta
    points = [[round(x+radius*np.cos(a),0),round(y+radius*np.sin(a),0)] for a in theta]
    return np.array(points, np.int32)

def test_area():
    height = 400
    width =400
    channels = 3
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea cuadrado
    cv2.rectangle(img, (0,0),(100,100), (255,255,255), -1)
    cv2.rectangle(img, (150,150),(200,200), (255,0,255), -1)
    cv2.rectangle(img, (200,0),(210,10), (255,255,0), -1)
    areas = [100,2500,10000]
    data = contour_segmentation(img)
    for cnt in data:
        print((cnt.get_area() in areas))    
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea rectangulos
    cv2.rectangle(img, (0,0),(140,100), (255,255,255), -1)
    #1.4
    cv2.rectangle(img, (150,150),(250,200), (255,0,255), -1)
    #2 rectangle considera el pixel final como perteneciente a rectangulo a dibujar.
    cv2.rectangle(img, (200,0),(220,10), (255,255,0), -1)
    #2
    areas = [14000,5000,200]
    data = contour_segmentation(img)
    for cnt in data:
        print((cnt.get_area() in areas)) 
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    img = np.zeros((height,width,channels), dtype=np.uint8)

    #se testea circulos
    cv2.circle(img, (10,10),10, (255,255,255), -1,cv2.FILLED)
    cv2.circle(img, (150,150),40, (255,0,255), -1,cv2.FILLED)
    cv2.circle(img, (300,50),50, (255,255,0), -1,cv2.FILLED)
    data = contour_segmentation(img)
    areas = np.pi*np.array([10*10,40*40,50*50])
    print(areas)
    for cnt in data:
        #TODO Assert with error.
        print(cnt.get_area())
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img = np.zeros((height,width,channels), dtype=np.uint8)
    #triangulos de alto 100 y base 100
    pts = np.array([[100,100],[100,200],[200,200]])
    print(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250],[350,250],[300,350]])
    print(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260]])
    print(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    data = contour_segmentation(img)
    for cnt in data:
        assert(cnt.get_area()==5000)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    areas = []
    img = np.zeros((height,width,channels), dtype=np.uint8)

    pts = np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32)
    areas.append(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250],[300,300], [350,250],[320,200],[280,200]], np.int32)
    areas.append(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260], [60,200]], np.int32)
    areas.append(math_area(pts))
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    data = contour_segmentation(img)
    
    for cnt in data:
        #revisar diagonales dificiles
        assert(cnt.get_area() in areas)
    cv2.imshow("blank_image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    archivo = open("test_area.txt", 'w')
    for i in range(3,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(i,(200,200),100)
        area_math = math_area(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        cv2.imshow("blank_image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        data = contour_segmentation(img)
        print(f"poligono de {i} lados")
        print(f"area calculada de forma matematica: {area_math}")
        print(f"area calculada por el programa: {data[0].get_area()}")
        print(f"error: {(data[0].get_area()-area_math)/area_math}")
        archivo.write(f"poligono de {i} lados\narea calculada de forma matematica: {area_math}\narea calculada por el programa: {data[0].get_area()}\nerror: {(data[0].get_area()-area_math)/area_math}\n")
    archivo.close()

def test_aspect_ratio():
    height = 400
    width =400
    channels = 3
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea cuadrado
    cv2.rectangle(img, (0,0),(100,100), (255,255,255), -1)
    cv2.rectangle(img, (150,150),(200,200), (255,0,255), -1)
    cv2.rectangle(img, (200,0),(210,10), (255,255,0), -1)
    data = contour_segmentation(img)
    #los cuadrados tienen ratio 1 siempre
    for cnt in data:
        assert(cnt.aspect_ratio() == 1)

    #se limpia la imagen.
    img = np.zeros((height,width,channels), dtype=np.uint8)
    #se testea rectangulos
    cv2.rectangle(img, (0,0),(140,100), (255,255,255), -1)
    cv2.rectangle(img, (150,150),(249,199), (255,0,255), -1)
    #rectangle considera el pixel final e inicial como perteneciente a rectangulo a dibujar, por lo que su aspect ratio es mayor.
    cv2.rectangle(img, (200,0),(219,9), (255,255,0), -1)
    data = contour_segmentation(img)
    aspect_ratios = [1.4, 2]
    for cnt in data:
        print(cnt.aspect_ratio())
        assert(cnt.aspect_ratio() in aspect_ratios)
    
    #se limpia la imagen.
    img = np.zeros((height,width,channels), dtype=np.uint8)

    #se testea circulos
    cv2.circle(img, (10,10),10, (255,255,255), -1)
    cv2.circle(img, (150,150),40, (255,0,255), -1)
    cv2.circle(img, (300,50),50, (255,255,0), -1)
    data = contour_segmentation(img)
    #todos los circulos son de ratio 1
    for cnt in data:
        assert(cnt.aspect_ratio() == 1)

    #se limpia la imagen
    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250],[350,250],[300,350]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    #los 3 triangulos tienen aspect ratio 1
    for cnt in data:
        assert(cnt.aspect_ratio() == 1)
    data = contour_segmentation(img)
    
    #se limpia la imagen
    img = np.zeros((height,width,channels), dtype=np.uint8)
    pts = np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[250,250], [350,250],[280,200],[300,300],[320,200]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    pts = np.array([[0,200],[0,300],[100,260], [60,220]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.fillPoly(img,[pts],(0,255,255))
    #poligonos de ratio 1
    for cnt in data:
        assert(cnt.aspect_ratio() == 1)

    archivo = open("test_ratio.txt", 'w')
    for i in range(3,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(3,(200,200),100)
        print(pts)
        ratio_math = math_aspect_ratio(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        print(f"poligono de {i} lados")
        print(f"ratio calculado de forma matematica: {ratio_math}")
        print(f"ratio calculado por el programa: {data[0].aspect_ratio()}")
        print(f"error: {(data[0].aspect_ratio()-ratio_math)/ratio_math}")
        archivo.write(f"poligono de {i} lados\nratio calculado de forma matematica: {ratio_math}\nratio calculado por el programa: {data[0].aspect_ratio()}\nerror: {(data[0].aspect_ratio()-ratio_math)/ratio_math}\n")
    archivo.close()

#test_area()
test_aspect_ratio()

#pts = np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32)
#print(math_aspect_ratio(pts))

