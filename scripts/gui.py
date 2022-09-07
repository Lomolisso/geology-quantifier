import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import pyvista

import image_managers


# FUNCIONES AUXILIARES
def choose_img():
    """
    Method to load image from a selected path, using windows file system UI.
    """
    # Ask for the image to load.
    global image
    image = image_managers.load_image_from_window()
    image = cv2.resize(image, (image.shape[1]*0.5, image.shape[0]*0.5))

    img2show = image
    im = Image.fromarray(img2show)
    img = ImageTk.PhotoImage(im)
    canvas.image = img
    canvas.create_image(0,0, image=img, anchor=NW)

def click_get_coords(event):
    canvas.old_coords = event.x, event.y
    
def drag(event):
    global crop_img
    canvas.new_coords = event.x, event.y
    canvas.delete('rect')
    canvas.create_rectangle(canvas.old_coords[0], canvas.old_coords[1],
                                            canvas.new_coords[0], canvas.new_coords[1], tags='rect')

def release(event):
    if canvas.coords('rect'):
        x0, y0, x1, y1 = canvas.coords('rect')
    else:
        x0, y0, x1, y1 = 0, 0, image.shape[1], image.shape[0]
    crop_img = image[int(y0) : int(y1), int(x0) : int(x1)]
    crop_img = cv2.resize(crop_img, (640, 480))
    crop_img2show = crop_img
    im = Image.fromarray(crop_img2show)
    img = ImageTk.PhotoImage(im)

    canvas_out.image = img
    canvas_out.create_image(0,0, image=img, anchor=NW)

def sphplot():
    mesh = pyvista.Sphere()
    mesh.plot(background="black")


# Inicializacion de ventana
window = Tk()
window.config(cursor='plus')
canvas = Canvas(window)
canvas_out = Canvas(window, width=640, height=480)
canvas.grid(column=0, row=1)
canvas_out.grid(column=1, row=1)

window.bind('<ButtonPress-1>', click_get_coords)
window.bind('<B1-Motion>', drag)
window.bind('<ButtonRelease-1>', release)

# Imagen a trabajar
image = None
crop_img = None

btnImg = Button(window, text='Choose image', width=20, command=choose_img, cursor='arrow')
btnImg.grid(column=0, row=0)

btn3D = Button(window, text='3D', width=20, command=sphplot, cursor='arrow')
btn3D.grid(row=0, column=1)

window.mainloop()

