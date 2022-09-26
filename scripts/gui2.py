import refactor_gui
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import image_managers, sample_extraction, percent, tube

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
    global img, canvas_frame, altWin, cropped_image_frame, images_with_clusters, img_tree
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
    image = image_managers.load_image_from_window()
    try:
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
            btnGoBack.grid(row=2, column=1)
            btnGoFor.grid(row=2, column=2)
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
    return 
    
            
def merge():
    global selected_images_indices, img_tree
    if len(selected_images_indices) < 2:
        messagebox.showwarning("Error", message="Por favor seleccionar más de una imagen.")
        return
    img_tree.merge(selected_images_indices)
    update_screen()
    selected_images_indices=[]
    return
        
    

def delete():
    global selected_images_indices, img_tree
    if len(selected_images_indices) == 0:
        messagebox.showwarning("Error", message="Por favor seleccionar al menos una imagen.")
        return
    img_tree.delete(selected_images_indices)
    update_screen()
    selected_images_indices=[]
    return
    global img, cropped_image_frame, selected_images
    imagen = img
    for key,val in selected_images.items():
        imagen = cv2.subtract(imagen,val[0])
        val[1].grid_remove()
    selected_images = {}
    img = imagen
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)

    canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
    fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_for_canva = Image.fromarray(fix_img)
    img_for_canva = ImageTk.PhotoImage(img_for_canva)
    canva.image = img_for_canva
    canva.create_image(0,0, image=img_for_canva, anchor=NW)
    canva.grid(row=1, column=1)




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
    global selected_images
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

def imageGoBack():
    return
    global current_image,selected_images, img,cropped_image_frame, canvas_frame
    # comingSoon()
    #Si la imagen actual es la primera no se puede retroceder
    if(current_image == 0):
        messagebox.showwarning("No se puede retroceder", message= "No hay más imágenes atras")
        return
    imgAnterior = images_with_clusters[current_image-1]
    pic = imgAnterior[0]
    list_of_clusters = imgAnterior[1:len(imgAnterior)]
    img = pic
    #Reemplazar la imagen actual por el cluster a separar
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)
    canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
    fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_for_canva = Image.fromarray(fix_img)
    img_for_canva = ImageTk.PhotoImage(img_for_canva)
    canva.image = img_for_canva
    canva.create_image(0,0, image=img_for_canva, anchor=NW)
    canva.grid(row=1, column=1)
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    #Actualizar imagen actual
    current_image -= 1
    #Resetear imagenes seleccionadas
    selected_images = {}
    #generar nuevos clusters
    cluster_len = 2
    for i in range(len(list_of_clusters)):
        imgClusterOrg = list_of_clusters[i]
        list_of_clusters[i] = cv2.resize(list_of_clusters[i], (int(list_of_clusters[i].shape[1]*0.7), int(list_of_clusters[i].shape[0]*0.7)))
        list_of_clusters[i] = cv2.cvtColor(list_of_clusters[i], cv2.COLOR_BGR2RGB)
        # name = " new cluster" + str(i)
        # cv2.imshow(name,cluster_masks[i])
        canva = Canvas(canvas_frame, width=list_of_clusters[i].shape[1], height=list_of_clusters[i].shape[0])
        
        im = Image.fromarray(list_of_clusters[i])
        imgg = ImageTk.PhotoImage(im)
        labelimg = Label(canva, image=imgg)
        labelimg.image = imgg
        labelimg.bind('<ButtonPress-1>', lambda event, image=imgClusterOrg, key=i, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        # canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)


def imageGoFor():
    return
    global current_image,selected_images, img,cropped_image_frame, canvas_frame
    # comingSoon()
    actual_len = len(list(images_with_clusters.keys()))
    #Si la imagen actual es la última no se puede avanzar
    if(current_image == actual_len - 1):
        messagebox.showwarning("No se puede avanzar", message= "No hay más imágenes adelante")
        return
    imgSgte = images_with_clusters[current_image+1]
    pic = imgSgte[0]
    list_of_clusters = imgSgte[1:len(imgSgte)]
    img = pic
    #Reemplazar la imagen actual por el cluster a separar
    cropped_image_frame.destroy()
    cropped_image_frame = Frame(window)
    cropped_image_frame.grid(row=1, column=1)
    canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
    fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_for_canva = Image.fromarray(fix_img)
    img_for_canva = ImageTk.PhotoImage(img_for_canva)
    canva.image = img_for_canva
    canva.create_image(0,0, image=img_for_canva, anchor=NW)
    canva.grid(row=1, column=1)
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    #Actualizar imagen actual
    current_image += 1
    #Resetear imagenes seleccionadas
    selected_images = {}
    #generar nuevos clusters
    cluster_len = 2
    for i in range(len(list_of_clusters)):
        imgClusterOrg = list_of_clusters[i]
        list_of_clusters[i] = cv2.resize(list_of_clusters[i], (int(list_of_clusters[i].shape[1]*0.7), int(list_of_clusters[i].shape[0]*0.7)))
        list_of_clusters[i] = cv2.cvtColor(list_of_clusters[i], cv2.COLOR_BGR2RGB)
        # name = " new cluster" + str(i)
        # cv2.imshow(name,cluster_masks[i])
        canva = Canvas(canvas_frame, width=list_of_clusters[i].shape[1], height=list_of_clusters[i].shape[0])
        
        im = Image.fromarray(list_of_clusters[i])
        imgg = ImageTk.PhotoImage(im)
        labelimg = Label(canva, image=imgg)
        labelimg.image = imgg
        labelimg.bind('<ButtonPress-1>', lambda event, image=imgClusterOrg, key=i, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        # canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)
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
img = None
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
btnGoBack = Button(btns_frame, text='<-', width=20, command=imageGoBack, cursor='arrow')
btnGoBack['font'] = myFont
#boton para avanzar en las imagenes creadas con clusters
btnGoFor = Button(btns_frame, text='->', width=20, command=imageGoFor, cursor='arrow')
btnGoFor['font'] = myFont

mainloop()

