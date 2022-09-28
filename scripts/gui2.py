from sqlalchemy import column
import refactor_gui
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import image_managers, sample_extraction, percent, tube, segmentacion_contorno as sc

# FUNCIONES AUXILIARES
CLUSTER_RESHAPE = 0.7
IMAGE_RESHAPE = 0.7

def update_screen():
    global cropped_image_frame, canvas_frame, img_tree, current_image

    for wget in canvas_frame.winfo_children():
        wget.destroy()
    
    # buscar una mejor manera resetear size del frame para imagenes
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)
    canvas_frame.grid_forget()
    canvas_frame.grid(row=1, column=2, columnspan=2)
    
    # Imagen del nodo actual
    img = img_tree.image

    # Set image for cropped image frame
    canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
    fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_for_canva = Image.fromarray(fix_img)
    img_for_canva = ImageTk.PhotoImage(img_for_canva)
    canva.image = img_for_canva
    canva.create_image(0,0, image=img_for_canva, anchor=NW)
    canva.grid(row=1, column=1)

    img_row_shape = 2
    i = 0
    for child in img_tree.childs:
        child_img = cv2.resize(child.image, (int(child.image.shape[1]*CLUSTER_RESHAPE), int(child.image.shape[0]*CLUSTER_RESHAPE)))
        child_img = cv2.cvtColor(child_img, cv2.COLOR_BGR2RGB)
        canva = Canvas(canvas_frame, width=child_img.shape[1], height=child_img.shape[0])
        
        photo_img = Image.fromarray(child_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        labelimg = Label(canva, image=img_for_label)
        labelimg.image = img_for_label
        labelimg.bind('<ButtonPress-1>', lambda event, image=child.image, key=i, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        canva.grid(row=1+i//img_row_shape, column=i%img_row_shape)
        i+=1
    

def show_img():
    global org_img, canvas_frame, altWin, cropped_image_frame, images_with_clusters, img_tree
    # Clean window
    if altWin:
        altWin.destroy()
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    
    # buscar una mejor manera resetear size del frame para imagenes
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)
    canvas_frame.grid_forget()
    # canvas_frame = Frame(window)
    canvas_frame.grid(row=1, column=2, columnspan=2)
    #Resetear imagenes con cluster al seleccionar nueva imagen
    images_with_clusters = {}
    current_image = 0
    # hasta aca
    window.withdraw()
    try:
        image = image_managers.load_image_from_window()
        img = sample_extraction.extract_sample(image)
        #parámetros para resize
        min_width = 600
        min_heigth = 300
        #TODO resize the image to a common shape
        if img.shape[0] < 400:
            img = cv2.resize(img, (int(img.shape[1] * min_width/img.shape[0]), min_width))
        if img.shape[1] < 200:      
            img = cv2.resize(img, (min_heigth, int(img.shape[0] * min_heigth/img.shape[1])))
        else:
            img = cv2.resize(img, (int(img.shape[1]*IMAGE_RESHAPE), int(img.shape[0]*IMAGE_RESHAPE)))

        org_img = img
        img_tree = refactor_gui.ImageNode(None, img)
        
        # Guardar la imagen original en el diccionario de imagenes con cluster en la última posición
        # y la posición como llave
        # actual_len = len(list(images_with_clusters.keys()))
        # images_with_clusters.update({actual_len: [img] })
        # Set image for cropped image frame
        update_screen()
                
        if isinstance(img, np.ndarray):
            btn3D.grid(row=0, column=1)
            num_of_cluster.grid(row=0, column=2)
            btnSplit.grid(row=0, column=3)
            btnMerge.grid(row=0, column=4)
            btnSub.grid(row=0, column=5)
            btnUp.grid(row=1, column=2)
            btnDown.grid(row=1, column=3)
            btnUndo.grid(row=1,column=0)
            btnContour.grid(row = 1, column = 4)
    except:
        pass
    window.deiconify()

# separacion y nuevo clustering sobre imagen seleccionada
def split():
    global selected_images_indices, img_tree, num_of_cluster
    n_childs = int(num_of_cluster.get())
    if len(selected_images_indices) > 1:
        messagebox.showwarning("Error", message="Por favor seleccionar solo una imagen.")
        return
    if len(selected_images_indices) ==1:
        img_tree = img_tree.childs[selected_images_indices[0]]
    
    img_tree.split(n_childs)
    update_screen()
    selected_images_indices=[]

            
def merge():
    global selected_images_indices, img_tree
    if len(selected_images_indices) < 2:
        messagebox.showwarning("Error", message="Por favor seleccionar más de una imagen.")
        return
    img_tree.merge(selected_images_indices)
    update_screen()
    selected_images_indices=[]
    

def delete():
    global selected_images_indices, img_tree
    if len(selected_images_indices) == 0:
        messagebox.showwarning("Error", message="Por favor seleccionar al menos una imagen.")
        return
    img_tree.delete(selected_images_indices)
    update_screen()
    selected_images_indices=[]

# plotear panoramica sobre cilindro 3D            
def plot3d():
    global altWin, img_tree, window
    img = img_tree.image
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
    global selected_images_indices
    # print(selected_images)
    if key in selected_images_indices:
        selected_images_indices.remove(key)
        canvas.configure(bg='white')
        for widget in canvas.winfo_children():
            if widget.cget("text"):
                widget.destroy()

    else:
        selected_images_indices.append(key)
        canvas.configure(bg='red')

        widgetP = Label(canvas, text=str(percent.percent(image)), fg='white', bg='black')
        widgetP.grid(row = 1,column=0 )

        widgetC = Label(canvas, text=str(percent.contour(image)), fg='white', bg='black')
        widgetC.grid(row = 2,column=0 )
    

def undo():
    global org_img, img_tree, selected_images_indices
    img_tree = refactor_gui.ImageNode(None,org_img)
    selected_images_indices = []
    update_screen()

def down():
    global selected_images_indices, img_tree
    if len(selected_images_indices) != 1:
        messagebox.showwarning("Error", message="Por favor seleccionar una imagen.")
        return
    img_tree = img_tree.childs[selected_images_indices[0]]
    selected_images_indices = []
    update_screen()

def up():
    global selected_images_indices, img_tree
    if img_tree.parent == None:
        messagebox.showwarning("Error", message="Esta es la imagen original.")
        return
    img_tree = img_tree.parent
    selected_images_indices = []
    update_screen()

def segmentate():
    global img_tree, selected_images_indices

    if len(selected_images_indices) > 1:
        messagebox.showwarning("Error", message="Por favor seleccionar solo una imagen.")
        return
    if len(selected_images_indices) ==1:
        img_tree = img_tree.childs[selected_images_indices[0]]
    update_screen()
    selected_images_indices = []
    contour = sc.contour_segmentation(img_tree.image) 
    sc.contour_agrupation(contour)
    segmentated = sc.cluster_segmentation(img_tree.image,contour)
    child_img = segmentated
    child_img = cv2.cvtColor(child_img, cv2.COLOR_BGR2RGB)
    canva = Canvas(canvas_frame, width=child_img.shape[1], height=child_img.shape[0])
    
    photo_img = Image.fromarray(child_img)
    img_for_label = ImageTk.PhotoImage(photo_img)
    labelimg = Label(canva, image=img_for_label)
    labelimg.image = img_for_label
    labelimg.bind('<ButtonPress-1>', lambda event, image=segmentated, key=0, canvas=canva: click(event, image, key, canvas))
    labelimg.grid(row=0, column=0, padx=10, pady=10)
    canva.grid()
    
    
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
btns_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=NW)
canvas_frame.grid(row=1, column=2, columnspan=2)
cropped_image_frame.grid(row=1, column=1)

# Arbol con imagenes
img_tree = None

# Tamaño de letra en botones
myFont = font.Font(size=13)

#Imagenes seleccionadas
selected_images_indices = []
#Imagen actual
current_image = 0
# variable globales
org_img = None
altWin = None

btnImg = Button(btns_frame, text='Seleccionar imagen', width=20, command=show_img, cursor='arrow')
btnImg.grid(row=0, column=0)
btnImg['font'] = myFont

btn3D = Button(btns_frame, text='3D', width=20, command=plot3d, cursor='arrow')
btn3D['font'] = myFont

num_of_cluster = Entry(btns_frame)
num_of_cluster['font'] = myFont
num_of_cluster.insert(0, "Número de clusters")
num_of_cluster.bind("<1>", lambda _ : num_of_cluster.delete(0,'end'))

btnSplit = Button(btns_frame, text='Separar', width=20, command=split, cursor='arrow')
btnSplit['font'] = myFont
btnMerge = Button(btns_frame, text='Combinar', width=20, command=merge, cursor='arrow')
btnMerge['font'] = myFont
btnSub = Button(btns_frame, text='Eliminar', width=20, command=delete, cursor='arrow')
btnSub['font'] = myFont
#boton para retroceder en las imagenes creadas con clusters
btnUp = Button(btns_frame, text='up', width=20, command=up, cursor='arrow')
btnUp['font'] = myFont
#boton para avanzar en las imagenes creadas con clusters
btnDown = Button(btns_frame, text='down', width=20, command=down, cursor='arrow')
btnDown['font'] = myFont

btnUndo = Button(btns_frame, text='undo', width=20, command=undo, cursor='arrow')
btnUndo['font'] = myFont

btnContour = Button(btns_frame, text='Segmentar', width=20, command=segmentate, cursor='arrow')
btnContour['font'] = myFont

mainloop()

