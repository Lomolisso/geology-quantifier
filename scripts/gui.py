from glob import glob
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np

import image_managers, sample_extraction, contorno_meanshift, percent, tube

# FUNCIONES AUXILIARES
def show_img():
    global img, canvas_frame, altWin, cropped_image_frame
    # Clean window
    if altWin:
        altWin.destroy()
    for wget in canvas_frame.winfo_children():
        wget.destroy()

    # buscar una mejor manera resetear size del frame para imagenes
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)
    canvas_frame.destroy()
    canvas_frame = Frame(window)
    canvas_frame.grid(row=1, column=2, columnspan=2)
    # hasta aca
    window.withdraw()
    image = image_managers.load_image_from_window()
    img = sample_extraction.extract_sample(image)
    #TODO resize the image to a common shape
    img = cv2.resize(img, (int(img.shape[1]*0.7), int(img.shape[0]*0.7)))
    cv2.destroyAllWindows()

    # Set image for cropped image frame
    canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
    img_for_canva = Image.fromarray(img)
    img_for_canva = ImageTk.PhotoImage(img_for_canva)
    canva.image = img_for_canva
    canva.create_image(0,0, image=img_for_canva, anchor=NW)
    canva.grid(row=1, column=1)
    
    
    if isinstance(img, np.ndarray):
        img2show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img2show)
        img4lbl = ImageTk.PhotoImage(im)
        # CroppedImgWindow(img4lbl)
        num_of_cluster.grid(row=0, column=2)
        btnCluster.grid(row=0, column=3)
        btnSplit.grid(row=0, column=4)
        btnMerge.grid(row=0, column=5)
    window.deiconify()

def get_percents():
    global img, selected_images

    # Dictionary to store the cluster images
    selected_images = {}
    # Destroy current cluster images
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    # Get cluster num from GUI   
    cluster_num = int(num_of_cluster.get())
    # Get mask using kmeans
    cluster_masks = contorno_meanshift.gen_masks(img, cluster_num)

    # Show the masks
    cluster_len = 2 #TODO set a valua depending on the image sizes
    for i in range(len(cluster_masks)):
        cluster_masks[i] = cv2.resize(cluster_masks[i], (int(cluster_masks[i].shape[1]*0.5), int(cluster_masks[i].shape[0]*0.5)))
        cluster_masks[i] = cv2.cvtColor(cluster_masks[i], cv2.COLOR_BGR2RGB)
        canva = Canvas(canvas_frame, width=cluster_masks[i].shape[1], height=cluster_masks[i].shape[0])
        canva.bind('<ButtonPress-1>', lambda event, image=cluster_masks[i], key=i, canvas=canva: click(event, image, key, canvas))
        im = Image.fromarray(cluster_masks[i])
        imgg = ImageTk.PhotoImage(im)
        canva.image = imgg
        canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)

# separacion y nuevo clustering sobre imagen seleccionada
def split():
    global selected_images

    comingSoon()
    return
    
    # for pic in selected_images.values():
    dict2list = list(selected_images.values())
    pic = dict2list[0]
    miniWin = Toplevel(window)
    miniWin.title("new cluster")
    miniWin.attributes('-toolwindow', True)
    cluster_num = int(num_of_cluster.get())
    cluster_masks = contorno_meanshift.gen_masks(pic, cluster_num)

    cluster_len = 5 # hardcodeado por mientras, saludos
    for i in range(len(cluster_masks)):
        cluster_masks[i] = cv2.resize(cluster_masks[i], (int(cluster_masks[i].shape[1]*0.7), int(cluster_masks[i].shape[0]*0.7)))
        cluster_masks[i] = cv2.cvtColor(cluster_masks[i], cv2.COLOR_BGR2RGB)
        canva = Canvas(miniWin, width=cluster_masks[i].shape[1], height=cluster_masks[i].shape[0])
        im = Image.fromarray(cluster_masks[i])
        imgg = ImageTk.PhotoImage(im)
        canva.image = imgg
        canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)
            
def merge():
    comingSoon()
    return

# plotear panoramica sobre cilindro 3D            
def plot3d():
    global altWin, img, window
    # Clean window
    if altWin:
        altWin.destroy()

    # If there isn't an image available
    if not isinstance(img, np.ndarray):
        # Load image using OS file window
        raw_img = image_managers.load_image_from_window()

        # Cut the img to analize an specific part of it.
        img = sample_extraction.extract_sample(raw_img)
    
    cv2.destroyAllWindows()
    if isinstance(img, np.ndarray):
        # Use the loaded img to fill a 3D tube surface.
        tube.fill_tube(img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# funcion para evento click sobre imagenes
def click(event, image, key, canvas):
    global selected_images
    if key in selected_images.keys():
        selected_images.pop(key)
        canvas.configure(bg='white')
    else:
        selected_images.update({key : image})
        canvas.configure(bg='red')
    
# funcion para crear una ventanita donde se vea el recorte original
def CroppedImgWindow(im):
    global altWin
    # Toplevel object which will
    # be treated as a new window
    altWin = Toplevel(window)
    # sets the title of the
    # Toplevel widget
    altWin.title("Cropped image")
  
    # A Label widget to show in toplevel
    lblImg = Label(altWin,
          image=im)

    lblImg.image = im
    lblImg.pack(fill=BOTH, expand=True)
    
def comingSoon():
    messagebox.showinfo("Proximamente", message="En desarrollo")


# Inicializacion de ventana
window = Tk()
window.title("Cuantificador geologico")
window.iconbitmap("icon.ico")
window.config(cursor='plus')
btns_frame = Frame(window)
canvas_frame = Frame(window)
cropped_image_frame = Frame(window)
btns_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10)
canvas_frame.grid(row=1, column=2, columnspan=2)
cropped_image_frame.grid(row=1, column=1)

myFont = font.Font(size=18)

#Imagenes seleccionadas
selected_images = {}

# variable globales
img = None
altWin = None

btnImg = Button(btns_frame, text='Seleccionar imagen', width=20, command=show_img, cursor='arrow')
btnImg.grid(row=0, column=0)
btnImg['font'] = myFont

btnCluster = Button(btns_frame, text='Generar Clusters', width=20, command=get_percents, cursor='arrow')
btnCluster['font'] = myFont
num_of_cluster = Entry(btns_frame)
num_of_cluster['font'] = myFont
num_of_cluster.insert(0, "Número de clusters")
num_of_cluster.bind("<1>", lambda _ : num_of_cluster.delete(0,'end'))


btn3D = Button(btns_frame, text='3D', width=20, command=plot3d, cursor='arrow')
btn3D.grid(row=0, column=1)
btn3D['font'] = myFont

btnSplit = Button(btns_frame, text='Separar', width=20, command=split, cursor='arrow')
btnSplit['font'] = myFont
btnMerge = Button(btns_frame, text='Combinar', width=20, command=merge, cursor='arrow')
btnMerge['font'] = myFont

if not img:
    btnCluster.grid_remove()
    num_of_cluster.grid_remove()
    btnCluster.grid_remove()

mainloop()

