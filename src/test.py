import numpy as np
import cv2
from shape_detection import contour_segmentation, ContourData

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
        return np.round(1/2*(detizq-detder),2)
    else: 
        return np.round(-1/2*(detizq-detder),2)

def math_aspect_ratio(array):
    maxx=max(fila[0] for fila in array)
    minx=min(fila[0] for fila in array)
    maxy=max(fila[1] for fila in array)
    miny=min(fila[1] for fila in array)
    x = maxx-minx+1
    y = maxy-miny+1
    ratio = x/y
    if ratio<1:
        ratio = 1/ratio
    return np.round(ratio, 2)

def math_equiv_radio(array):
    return np.sqrt(math_area(array)/np.pi)

def math_equiv_length(array):
    return np.round(np.sqrt(math_area(array)/math_aspect_ratio(array)), 1)

def math_middle_point(array):
    maxx=max(fila[0] for fila in array)
    x=min(fila[0] for fila in array)
    maxy=max(fila[1] for fila in array)
    y=min(fila[1] for fila in array)
    h =maxy-y
    w = maxx-x
    return (np.round(x+w/2,0), np.round(y+h/2,0))

def poli_gen(n, center, radius):
    x, y = center
    theta = np.sort(np.random.rand(n))
    theta = 2*np.pi*theta
    points = [[round(x+radius*np.cos(a),0),round(y+radius*np.sin(a),0)] for a in theta]
    return np.array(points, np.int32)

def poli_gen_radio(n, center, radio, min):
    x, y = center
    theta = np.sort(np.random.uniform(0,1,n))
    theta = 2*np.pi*theta
    ran = radio*np.random.uniform(min,1,n)
    points = [[round(x+ran[i]*np.cos(theta[i]),0),round(y+ran[i]*np.sin(theta[i]),0)] for i in range(len(theta))]
    return np.array(points, np.int32)

def assert_error_tuple(estimate_value: tuple, calculated_value: tuple, error:float):
    est_x, est_y = estimate_value
    cal_x, cal_y = calculated_value
    error_calculado = (cal_x-est_x)/est_x
    assert(error>abs(error_calculado))
    error_calculado = (cal_y-est_y)/est_y
    assert(error>abs(error_calculado))

def assert_error_float(estimate_value: np.float64, calculated_value: np.float64, error:float):
    error_calculado = (calculated_value-estimate_value)/estimate_value
    assert(error>abs(error_calculado))

def assert_error(estimate_value, calculated_value, error:float):
    if type(estimate_value)==tuple:
        assert_error_tuple(estimate_value, calculated_value, error)
    else:
        assert_error_float(estimate_value, calculated_value, error)

def testing(funcion_programa, funcion_math, error):
    height = 400
    width =400
    channels = 3
    
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
        assert_error(value, funcion_programa(data[0]), error)
    
    for i in range(10,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen(i,(200,200),100)
        value = funcion_math(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        try: 
            assert_error(value, funcion_programa(data[0]), error)
        except:
            cv2.imshow(f"{funcion_programa}", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    for i in range(10,100):
        img = np.zeros((height,width,channels), dtype=np.uint8)
        pts = poli_gen_radio(i,(200,200),100, 0.8)
        value = funcion_math(pts)
        pts = pts.reshape((-1,1,2))
        img = cv2.fillPoly(img,[pts],(0,255,255))
        data = contour_segmentation(img)
        try: 
            assert_error(value, funcion_programa(data[0]), error)
        except:
            cv2.imshow(f"{funcion_programa}", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

i = 0
while(i<=100):
    testing(ContourData.get_area, math_area, 0.05)
    testing(ContourData.aspect_ratio, math_aspect_ratio, 0.01)
    testing(ContourData.get_equiv_radius,math_equiv_radio, 0.05)
    testing(ContourData.get_equiv_lenght, math_equiv_length, 0.01)
    testing(ContourData.get_middle_point, math_middle_point, 0.01)
    i +=1
