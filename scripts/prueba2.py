from matplotlib.cm import get_cmap

import pyvista as pv
from pyvista import examples
import api_fm

img,filename = api_fm.load_image()

tex = pv.read_texture(filename)


# create a surface to host this texture
surf = pv.read('.\scripts\\tubo.obj')

surf.plot(texture=tex)