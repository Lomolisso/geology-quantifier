"""
Script to generate and show a 3D tube, filling its surface with
a texture. Try to use a panoramic image.
You can do it calling fill_tube(texture_img), the image must be
a matrix.
"""
import cv2
import pyvista as pv


def fill_tube(image):
    out = cv2.flip(image, 1)
    outRGB = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    tex = pv.numpy_to_texture(outRGB)
    #Creamos el tubo y luego cargamos sobre él la textura, para
    #luego visualizarlo
    surf = pv.read('.\scripts\\tubo.obj')
    surf.plot(texture=tex, background="black")
    return True
