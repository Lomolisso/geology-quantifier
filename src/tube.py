"""
Script to generate and show a 3D tube, filling its surface with
a texture. Try to use a panoramic image.
You can do it calling fill_tube(texture_img), the image must be
a matrix.
"""
import cv2
import pyvista as pv

pv.global_theme.title = '3D Rock Sample'


def fill_tube(image: cv2.Mat) -> bool:
    """
    Fills a 3D tube surface with an image 
    given as an input.
    """
    out = cv2.flip(image, 1)
    outRGB = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    tex = pv.numpy_to_texture(outRGB)

    # Create the tube and later load the image texture, to see it.
    surf = pv.read('.\src\\tubo.obj')
    surf.plot(texture=tex, background="black", cpos='xy')
    return True
