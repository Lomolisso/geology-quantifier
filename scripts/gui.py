import cv2
from tkinter import *
from PIL import Image, ImageTk

import image_managers, sample_extraction, contorno_meanshift, percent, tube

# String to identify the prints of this file
TOKEN = "[IMG_MAN]"

# FUNCIONES AUXILIARES
def show_img():
    global img
    global canvas_frame
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    # buscar una mejor manera resetear size del frame para imagenes
    canvas_frame.destroy()
    canvas_frame = Frame(window)
    canvas_frame.grid(row=1, columnspan=3)
    # hasta aca
    window.withdraw()
    image = image_managers.load_image_from_window()
    img = sample_extraction.extract_sample(image)
    num_of_cluster.grid(row=0, column=1)
    btnCluster.grid(row=0, column=2)
    window.deiconify()

def get_percents():
    global img
    for wget in canvas_frame.winfo_children():
        wget.destroy()    
    cluster_num = int(num_of_cluster.get())
    # Get mask using kmeans
    cluster_masks = contorno_meanshift.gen_masks(img, cluster_num)

    # Show the masks
    cluster_len = len(cluster_masks)//2
    for i in range(len(cluster_masks)):
        cluster_masks[i] = cv2.resize(cluster_masks[i], (int(cluster_masks[i].shape[1]*0.7), int(cluster_masks[i].shape[0]*0.7)))
        canva = Canvas(canvas_frame, width=cluster_masks[i].shape[1], height=cluster_masks[i].shape[0])
        canva.bind('<ButtonPress-1>', lambda event, image=cluster_masks[i], tag=i: click(event, image, tag))
        im = Image.fromarray(cluster_masks[i])
        imgg = ImageTk.PhotoImage(im)
        canva.image = imgg
        canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)

def plot3d():
    # Load image using OS file window
	raw_img = image_managers.load_image_from_window()

	# Cut the img to analize an specific part of it.
	img = sample_extraction.extract_sample(raw_img)

	# Use the loaded img to fill a 3D tube surface.
	tube.fill_tube(img)

def click(event, image, tag):
    print(image)

# Inicializacion de ventana
window = Tk()
window.config(cursor='plus')
btns_frame = Frame(window)
canvas_frame = Frame(window)
btns_frame.grid(row=0, column=1)
canvas_frame.grid(row=1, columnspan=3)

#Imagenes
images = {}

# Imagen a trabajar
img = None

btnImg = Button(btns_frame, text='Seleccionar imagen', width=20, command=show_img, cursor='arrow', padx=10, pady=10)
btnImg.grid(row=0, column=0)

btnCluster = Button(btns_frame, text='cluster', width=20, command=get_percents, cursor='arrow')
num_of_cluster = Entry(btns_frame)

btn3D = Button(btns_frame, text='3D', width=20, command=plot3d, cursor='arrow')
btn3D.grid(row=0, column=4)

if not img:
    btnCluster.grid_remove()
    num_of_cluster.grid_remove()


window.mainloop()

