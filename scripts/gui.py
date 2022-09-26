from ctypes.wintypes import tagPOINT
from glob import glob
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np

import image_managers, sample_extraction, contorno_meanshift, percent, tube

# FUNCIONES AUXILIARES
def show_img():
    global img, canvas_frame, altWin, cropped_image_frame, images_with_clusters
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
            img = cv2.resize(img, (int(img.shape[1]*0.7), int(img.shape[0]*0.7)))
        cv2.destroyAllWindows()
        #Guardar la imagen original en el diccionario de imagenes con cluster en la última posición
        #y la posición como llave
        actual_len = len(list(images_with_clusters.keys()))
        images_with_clusters.update({actual_len: [img] })
        # Set image for cropped image frame
        canva = Canvas(cropped_image_frame, width=img.shape[1], height=img.shape[0])
        fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_for_canva = Image.fromarray(fix_img)
        img_for_canva = ImageTk.PhotoImage(img_for_canva)
        canva.image = img_for_canva
        canva.create_image(0,0, image=img_for_canva, anchor=NW)
        canva.grid(row=1, column=1)
        
        
        if isinstance(img, np.ndarray):
            btn3D.grid(row=0, column=1)
            num_of_cluster.grid(row=0, column=2)
            btnCluster.grid(row=0, column=3)
            btnSplit.grid(row=0, column=4)
            btnMerge.grid(row=0, column=5)
            btnSub.grid(row=0, column=6)
            btnGoBack.grid(row=2, column=1)
            btnGoFor.grid(row=2, column=2)
    except:
        pass
    window.deiconify()
    

def get_percents():
    global img, selected_images, images_with_clusters

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
    #Eliminar los clusters antiguos
    images_with_clusters[current_image] = [images_with_clusters[current_image][0]]
    for i in range(len(cluster_masks)):
        imgClusterOrg = cluster_masks[i]
        #Agregar los clusters a la imagen actual dentro del diccionario de imágen con clusters para la imagen actual
        images_with_clusters[current_image].append(cluster_masks[i])
        cluster_masks[i] = cv2.resize(cluster_masks[i], (int(cluster_masks[i].shape[1]*0.5), int(cluster_masks[i].shape[0]*0.5)))

        cluster_masks[i] = cv2.cvtColor(cluster_masks[i], cv2.COLOR_BGR2RGB)
        canva = Canvas(canvas_frame, width=cluster_masks[i].shape[1], height=cluster_masks[i].shape[0])
        
        im = Image.fromarray(cluster_masks[i])
        imgg = ImageTk.PhotoImage(im)
        labelimg = Label(canva, image=imgg)
        labelimg.image = imgg
        labelimg.bind('<ButtonPress-1>', lambda event, image=imgClusterOrg, key=i, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        # canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)

# separacion y nuevo clustering sobre imagen seleccionada
def split():
    global selected_images,images_with_clusters,current_image, img, cropped_image_frame, canvas_frame

    # comingSoon()
    # return
    
    # for pic in selected_images.values():
    #Solo puede haber una imagen seleccionada
    if(len(list(selected_images.keys())) != 1):
        messagebox.showwarning("Error", message="Por favor seleccionar solo una imagen.")
        return
    #Extraer la imagen seleccionada
    dict2list = list(selected_images.values())
    pic = dict2list[0][0]
    #Agregar el cluster seleccionado como nueva imagen al diccionario de imagen con cluster
    actual_len = len(list(images_with_clusters.keys()))
    images_with_clusters.update({actual_len:[pic]})

    cluster_num = int(num_of_cluster.get())
    cluster_masks = contorno_meanshift.gen_masks(pic, cluster_num)

    cluster_len = 2 # hardcodeado por mientras, saludos
    for wget in canvas_frame.winfo_children():
        wget.destroy()
    #Actualizar imagen acual
    current_image = actual_len
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
    #Resetear imagenes seleccionadas
    selected_images = {}
    #generar nuevos clusters
    for i in range(len(cluster_masks)):
        imgClusterOrg = cluster_masks[i]
        images_with_clusters[current_image].append(imgClusterOrg)
        cluster_masks[i] = cv2.resize(cluster_masks[i], (int(cluster_masks[i].shape[1]*0.7), int(cluster_masks[i].shape[0]*0.7)))
        cluster_masks[i] = cv2.cvtColor(cluster_masks[i], cv2.COLOR_BGR2RGB)
        # name = " new cluster" + str(i)
        # cv2.imshow(name,cluster_masks[i])
        canva = Canvas(canvas_frame, width=cluster_masks[i].shape[1], height=cluster_masks[i].shape[0])
        
        im = Image.fromarray(cluster_masks[i])
        imgg = ImageTk.PhotoImage(im)
        labelimg = Label(canva, image=imgg)
        labelimg.image = imgg
        labelimg.bind('<ButtonPress-1>', lambda event, image=imgClusterOrg, key=i, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        # canva.create_image(0,0, image=imgg, anchor=NW)
        canva.grid(row=1+i//cluster_len, column=i%cluster_len)
            
def merge():
    global selected_images
    imagen = np.zeros(img.shape, dtype='uint8')
    try:
        # canva1 = list(selected_images.values())[0][1]
        key1 = list(selected_images.keys())[0]
        column = key1 % 2
        row = (key1 // 2) + 1
        for key,val in selected_images.items():
            imagen = cv2.add(imagen,val[0])
            val[1].destroy()
        selected_images = {}
        imagenOrg = imagen
        imagen = cv2.resize(imagen, (int(imagen.shape[1]*0.5), int(imagen.shape[0]*0.5)))

        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        canva = Canvas(canvas_frame, width=imagen.shape[1], height=imagen.shape[0])
        im = Image.fromarray(imagen)
        imgg = ImageTk.PhotoImage(im)
        labelimg = Label(canva, image=imgg)
        labelimg.image = imgg
        labelimg.bind('<ButtonPress-1>', lambda event, image=imagenOrg, key=key1, canvas=canva: click(event, image, key, canvas))
        labelimg.grid(row=0, column=0, padx=10, pady=10)
        canva.grid(row=row, column=column)
    except:
        messagebox.showwarning("Error", message="Selecciona cluster por favor")
        
    

def substract():
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
    # print(selected_images)
    if key in selected_images.keys():
        selected_images.pop(key)
        canvas.configure(bg='white')
        for widget in canvas.winfo_children():
            if widget.cget("text"):
                widget.destroy()

    else:
        selected_images.update({key : [image, canvas]})
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

myFont = font.Font(size=13)

#Imagenes seleccionadas
selected_images = {}
#Imágenes junto a sus clusters
images_with_clusters = {}
#Imagen actual
current_image = 0
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
btn3D['font'] = myFont

btnSplit = Button(btns_frame, text='Separar', width=20, command=split, cursor='arrow')
btnSplit['font'] = myFont
btnMerge = Button(btns_frame, text='Combinar', width=20, command=merge, cursor='arrow')
btnMerge['font'] = myFont
btnSub = Button(btns_frame, text='Eliminar', width=20, command=substract, cursor='arrow')
btnSub['font'] = myFont
#boton para retroceder en las imagenes creadas con clusters
btnGoBack = Button(btns_frame, text='<-', width=20, command=imageGoBack, cursor='arrow')
btnGoBack['font'] = myFont
#boton para avanzar en las imagenes creadas con clusters
btnGoFor = Button(btns_frame, text='->', width=20, command=imageGoFor, cursor='arrow')
btnGoFor['font'] = myFont

if not img:
    btnCluster.grid_remove()
    num_of_cluster.grid_remove()
    btnCluster.grid_remove()

mainloop()

