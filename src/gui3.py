import csv
import datetime
import os
import refactor_gui
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import image_managers, sample_extraction, tube, segmentacion_contorno as sc
from utils import EntryWithPlaceholder

CLUSTER_RESHAPE = 0.5
    

class gui():
    def __init__(self, master) -> None:
        self.myFont = font.Font(size=13)
        self.main_win = master
        self.btns_fr = Frame(self.main_win)
        self.cropped_img_fr = Frame(self.main_win)
        self.canvas_fr = Frame(self.main_win)
        self.img_tree = None
        self.selected_images_indices = []
        self.org_img = None
        self.results_fr = Frame(self.main_win)
        self.btns_fr.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=NW)
        self.canvas_fr.grid(row=1, column=2, columnspan=2)
        self.cropped_img_fr.grid(row=1, column=1)
        self.results_fr.grid(row=2,column=1,sticky=S)

        self.btnImg = Button(self.btns_fr, text='Seleccionar imagen', width=20, command=self.show_img, cursor='arrow')
        self.btnImg.grid(row=0, column=0)
        self.btnImg['font'] = self.myFont

        self.btn3D = Button(self.btns_fr, text='3D', width=20, command=self.plot3d, cursor='arrow')
        self.btn3D['font'] = self.myFont

        self.num_of_cluster = EntryWithPlaceholder(self.btns_fr, "Número de clusters", 'gray')
        self.num_of_cluster['font'] = self.myFont

        self.btnSplit = Button(self.btns_fr, text='Separar', width=20, command=self.split, cursor='arrow')
        self.btnSplit['font'] = self.myFont
        self.btnMerge = Button(self.btns_fr, text='Combinar', width=20, command=self.merge, cursor='arrow')
        self.btnMerge['font'] = self.myFont
        self.btnSub = Button(self.btns_fr, text='Eliminar', width=20, command=self.delete, cursor='arrow')
        self.btnSub['font'] = self.myFont
        # #boton para retroceder en las imagenes creadas con clusters
        self.btnUp = Button(self.btns_fr, text='Subir', width=20, command=self.up, cursor='arrow')
        self.btnUp['font'] = self.myFont
        # #boton para avanzar en las imagenes creadas con clusters
        self.btnDown = Button(self.btns_fr, text='Bajar', width=20, command=self.down, cursor='arrow')
        self.btnDown['font'] = self.myFont

        self.btnUndo = Button(self.btns_fr, text='Deshacer', width=20, command=self.undo, cursor='arrow')
        self.btnUndo['font'] = self.myFont

        self.btnContour = Button(self.btns_fr, text='Segmentar', width=20, command=self.segmentate, cursor='arrow')
        self.btnContour['font'] = self.myFont

        self.btnSave = Button(self.btns_fr, text='Guardar', width=20, command=self.save, cursor='arrow')
        self.btnSave['font'] = self.myFont

        self.btnUpdate = Button(self.btns_fr, text='Actualizar', width=20, command=self.update_screen, cursor='arrow')
        self.btnUpdate['font'] = self.myFont

        
    def split(self):
        n_childs = int(self.num_of_cluster.get())
        if len(self.selected_images_indices) > 1:
            messagebox.showwarning("Error", message="Por favor seleccionar solo una imagen.")
            return
        if len(self.selected_images_indices) ==1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        
        self.img_tree.split(n_childs)
        self.update_screen()
        self.selected_images_indices=[]
    
    def show_img(self):
        self.main_win.withdraw()
        try:
            image = image_managers.load_image_from_window()
            img = sample_extraction.extract_sample(image)
            # MOVER ESTA FUNCIONALIDAD A OTRO LADO/FUNCION/METODO PARA TRABAJAR IMAGENES
            #TODO resize the image to a common shape
            # if img.shape[0] < 400:
            #     img = cv2.resize(img, (int(img.shape[1] * min_width/img.shape[0]), min_width))
            # if img.shape[1] < 200:      
            #     img = cv2.resize(img, (min_heigth, int(img.shape[0] * min_heigth/img.shape[1])))
            # else:
            #     img = cv2.resize(img, (int(img.shape[1]*IMAGE_RESHAPE), int(img.shape[0]*IMAGE_RESHAPE)))

            self.org_img = img
            self.img_tree = refactor_gui.ImageNode(None, img)
            
            # Guardar la imagen original en el diccionario de imagenes con cluster en la última posición
            # y la posición como llave
            # actual_len = len(list(images_with_clusters.keys()))
            # images_with_clusters.update({actual_len: [img] })
            # Set image for cropped image frame
            self.update_screen()
                    
            if isinstance(img, np.ndarray):
                self.btn3D.grid(row=0, column=1)
                self.num_of_cluster.grid(row=0, column=2)
                self.btnSplit.grid(row=0, column=3)
                self.btnMerge.grid(row=0, column=4)
                self.btnSub.grid(row=0, column=5)
                self.btnUndo.grid(row=1,column=0)
                self.btnSave.grid(row=1, column=1)
                self.btnUp.grid(row=1, column=2)
                self.btnDown.grid(row=1, column=3)
                self.btnContour.grid(row=1, column=4)
                self.btnUpdate.grid(row=1, column=5)
        except:
            pass
        self.main_win.deiconify()
        

    def clean_win(self):
        for wget in self.canvas_fr.winfo_children():
            wget.destroy()

        for wget in self.results_fr.winfo_children():
            wget.destroy()
        
        for wget in self.cropped_img_fr.winfo_children():
            wget.destroy()
        
        self.cropped_img_fr.destroy()
        self.cropped_img_fr = Frame(self.main_win)
        self.cropped_img_fr.grid(row=1, column=1)
        self.canvas_fr.destroy()
        self.canvas_fr = Frame(self.main_win)
        self.canvas_fr.grid(row=1, column=2, columnspan=2)
    
    def add_img_to_canvas(self, canvas, img):
        photo_img = Image.fromarray(img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        label_img = Label(canvas, image=img_for_label)
        label_img.image = img_for_label
        label_img.grid(row=0, column=0, padx=10, pady=10)
        return label_img
        
    def click(self, image, key, canvas):
        if key in self.selected_images_indices:
            self.selected_images_indices.remove(key)
            canvas.configure(bg='white')
            for widget in canvas.winfo_children():
                if widget.cget("text"):
                    widget.destroy()

        else:
            self.selected_images_indices.append(key)
            canvas.configure(bg='red')

    def resize_img(self, img):
        # Get actual window size
        win_height = self.main_win.winfo_height()
        win_width = self.main_win.winfo_width()

        resize_height = win_height * 1 // 2
        resize_width = win_width * 2 // 5

        # Height is related with img.shape[0]
        if img.shape[0] > img.shape[1]:
            resize_img = cv2.resize(img, ((int(img.shape[1] * resize_height / img.shape[0])), resize_height))
            if resize_img.shape[1] > resize_width:
                resize_img = cv2.resize(resize_img, (resize_width, int(resize_img.shape[0] * resize_width / resize_img.shape[1])))
        # Width is relates with img.shape[1]
        else:
            resize_img = cv2.resize(img, (resize_width, int(img.shape[0] * resize_width / img.shape[1])))
            if resize_img.shape[0] > resize_height:
                resize_img = cv2.resize(resize_img,  ((int(resize_img.shape[1] * resize_height / resize_img.shape[0])), resize_height))

        return resize_img

    def update_screen(self):
        self.clean_win()
        # Imagen del nodo actual
        img = self.img_tree.image
        self.selected_images_indices = []

        # Set image for cropped image frame
        img = self.resize_img(img)
        canva = Canvas(self.cropped_img_fr, width=img.shape[1], height=img.shape[0])
        fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _ = self.add_img_to_canvas(canva, fix_img)
        canva.grid(row=1, column=1)

        img_row_shape = 2
        i = 0
        for child in self.img_tree.childs:
            child_img = self.resize_img(child.image)
            child_img = cv2.resize(child.image, (int(child_img.shape[1]*CLUSTER_RESHAPE), int(child_img.shape[0]*CLUSTER_RESHAPE)))
            child_img = cv2.cvtColor(child_img, cv2.COLOR_BGR2RGB)
            canva = Canvas(self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0])
            label = self.add_img_to_canvas(canva, child_img)
            label.bind('<ButtonPress-1>', lambda event, image=child.image, key=i, canvas=canva: self.click(image, key, canvas))
            canva.grid(row=1+i//img_row_shape, column=i%img_row_shape)
            i+=1

    def merge(self):
        if len(self.selected_images_indices) < 2:
            messagebox.showwarning("Error", message="Por favor seleccionar más de una imagen.")
            return
        self.img_tree.merge(self.selected_images_indices)
        self.update_screen()
        self.selected_images_indices=[]

    def delete(self):
        if len(self.selected_images_indices) == 0:
            messagebox.showwarning("Error", message="Por favor seleccionar al menos una imagen.")
            return
        self.img_tree.delete(self.selected_images_indices)
        self.update_screen()
        self.selected_images_indices=[]

    # plotear panoramica sobre cilindro 3D            
    def plot3d(self):
        img = self.img_tree.image
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
        
    def undo(self):
        self.img_tree = refactor_gui.ImageNode(None,self.org_img)
        self.selected_images_indices = []
        self.update_screen()

    def down(self):
        if len(self.selected_images_indices) != 1:
            messagebox.showwarning("Error", message="Por favor seleccionar una imagen.")
            return
        self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        self.selected_images_indices = []
        self.update_screen()

    def up(self):
        if self.img_tree.parent == None:
            messagebox.showwarning("Error", message="Esta es la imagen original.")
            return
        self.img_tree = self.img_tree.parent
        self.selected_images_indices = []
        self.update_screen()

    
    def segmentate(self):
        if len(self.selected_images_indices) > 1:
            messagebox.showwarning("Error", message="Por favor seleccionar solo una imagen.")
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]

        self.update_screen()
        for wget in self.canvas_fr.winfo_children():
            wget.destroy()
        self.selected_images_indices = []
        

        contour = sc.contour_segmentation(self.img_tree.image) 
        sc.contour_agrupation(contour)
        segmentated = sc.cluster_segmentation(self.img_tree.image,contour)
        segmentated = self.resize_img(segmentated)
        child_img = segmentated
        child_img = cv2.cvtColor(child_img, cv2.COLOR_BGR2RGB)
        canva = Canvas(self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0])
        self.add_img_to_canvas(canva, child_img)
        canva.grid()

        results = sc.generate_results(contour)
        self.fill_table(results)

    def fill_table(self, results):
        label_color = Label(self.results_fr, text="Color")
        label_color.grid(row=0, column=0)
        label_name = Label(self.results_fr, text="Grupo")
        label_name.grid(row=0, column=1)
        label_total = Label(self.results_fr, text="Porcentaje Total")
        label_total.grid(row=0, column=2)
        label_prom = Label(self.results_fr, text="Porcentaje Promedio")
        label_prom.grid(row=0, column=3)
        
        for row_num in range(1, len(results[0])+1):
            (b, g, r) = sc.COLORS[row_num-1]
            color = '#%02x%02x%02x' % (r, g, b)
            label_color = Label(self.results_fr, bg=color, width=1, height=1, justify=CENTER)
            label_color.grid(row=row_num, column=0, sticky=W)
            
            name = EntryWithPlaceholder(self.results_fr, f"Grupo {row_num}")
            name['font'] = self.myFont
            name.grid(row=row_num, column=1)

            label_total = Label(self.results_fr, text=results[0][row_num-1])
            label_total.grid(row=row_num, column=2)

            label_prom = Label(self.results_fr, text=results[1][row_num-1])
            label_prom.grid(row=row_num, column=3)

        self.btnExport = Button(self.results_fr, text="Export to csv", width=15, command=self.table_to_csv, cursor='arrow')
        self.btnExport['font'] = self.myFont
        self.btnExport.grid(row=2, column=4)
    
    def table_to_csv(self):
        wgets = self.results_fr.winfo_children()[:-1]
        def wgetter(wget_arr):
            ret_arr = []
            for wget in wget_arr:
                if isinstance(wget, Entry):
                    ret_arr.append(wget.get())
                else:
                    if wget.cget('text') == '':
                        ret_arr.append(wget.cget('bg'))
                    else:
                        ret_arr.append(wget.cget('text'))
            return ret_arr
    
        rows = [wgetter(wgets[i:i+4]) for i in range(0, len(wgets), 4)]

        with open('geo_data.csv', 'w', newline='') as f:
            wrtr = csv.writer(f, delimiter=',')
            for row in rows:
                wrtr.writerow(row)
    
    def save(self):
        PATH = f"output/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        os.makedirs(PATH)
        image_managers.save_image_from_path(self.img_tree.image, f"{PATH}/original.png")
        for i in range(len(self.img_tree.childs)):
            image_managers.save_image_from_path(self.img_tree.childs[i].image, f"{PATH}/cluster_{i}.png")
        messagebox.showinfo("Guardado", message="Las imagenes se han guardado correctamente")

    
win = Tk()
win.title("Cuantificador geologico")
win.iconbitmap("icon.ico")
win.config(cursor='plus')
screen_width = win.winfo_screenwidth()
screen_height = win.winfo_screenheight()
win.geometry(f"{screen_width * 19 // 20}x{screen_height * 17 // 20}+0+0")
win.minsize(screen_width * 2 // 3, screen_height * 2 // 3)
win.maxsize(screen_width, screen_height)
gg = gui(win)        
win.mainloop()