import numpy as np
import cv2
import percent as pc
import random
from shape_detection import contour_segmentation, ContourData

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

def poli_gen_radio(n, center, radio_random):
    x, y = center
    theta = np.sort(np.random.rand(n))
    theta = 2*np.pi*theta
    radio = (radio_random+20)-radio_random*np.random.rand(n)
    points = [[round(x+radio[i]*np.cos(theta[i]),0),round(y+radio[i]*np.sin(theta[i]),0)] for i in range(len(theta))]
    return np.array(points, np.int32)

def assert_error(estimate_value, calculated_value, error):
    error_calculado = (calculated_value-estimate_value)/estimate_value
    print(error_calculado)
    assert(error>abs(error_calculado))

def testing(funcion_programa, funcion_math):
    height = 400
    width =400
    channels = 3
    lados = [10, 50, 100]
    
    points = []
    points.append(np.array([[100,100],[100,200],[200,200]]))
    points.append(np.array([[250,250],[350,250],[300,350]]))
    points.append(np.array([[0,200],[0,300],[100,260]]))
    points.append(np.array([[100,100],[100,200],[200,200],[150,150],[200,100]], np.int32))  
    points.append(np.array([[250,250],[300,300], [350,250],[320,200],[280,200]], np.int32))
    points.append(np.array([[0,200],[0,300],[100,260], [70,200]], np.int32))
    
    for pts in points:
        img = np.zeros((height,width,channels), dtype=np.uint8)
        value = funcion_math(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        #revisar diagonales dificiles
        assert_error(value, funcion_programa(data[0]), 0.02)
    
    for i in range(3,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(i,(200,200),100)
        value = funcion_math(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        assert_error(value, funcion_programa(data[0]), 0.02)
    while(True):
        for i in range(10,100):
            img = np.zeros((height,width,channels), dtype=np.uint8)
            pts = poli_gen_radio(i,(200,200),100)
            value = funcion_math(pts)
            pts = pts.reshape((-1,1,2))
            img = cv2.fillPoly(img,[pts],(0,255,255))
            
            data = contour_segmentation(img)
            value2 = [i[0] for i in data[0].contour]
            a = funcion_math(value2)
            try:
                assert_error(value, funcion_programa(data[0]), 0.1)
            except:
                cv2.imshow("a",img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        

testing(ContourData.get_area, math_area)

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
        assert((cnt.get_area() in areas))

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
        assert((cnt.get_area() in areas)) 
    

    #se testea circulos
    areas = np.pi*np.array([10*10,40*40,50*50])
    radio = range(10, 150, 10)
    for r in radio:
        img = np.zeros((height,width,channels), dtype=np.uint8)
        cv2.circle(img, (200,200),r, (255,255,255), -1,cv2.FILLED)
        data = contour_segmentation(img)
        area_math = np.pi*r*r
        assert_error(area_math,data[0].get_area(), 0.02)


    archivo = open("test_area.txt", 'w')
    archivo.write("lados,area_matematica,area_programa,error\n")
    for i in range(3,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(i,(200,200),100)
        area_math = math_area(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        archivo.write(f"{i},{area_math},{data[0].get_area()},{(data[0].get_area()-area_math)/area_math}\n")
        
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
    archivo.write("lados,ratio_matematico,ratio_programa,error\n")
    for i in range(3,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(3,(200,200),100)
        print(pts)
        ratio_math = math_aspect_ratio(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        archivo.write(f"{i},{ratio_math},{data[0].aspect_ratio()},{(data[0].aspect_ratio()-ratio_math)/ratio_math}\n")
    archivo.close()

#test_area()
#test_aspect_ratio()


