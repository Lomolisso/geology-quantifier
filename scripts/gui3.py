import csv

import refactor_gui
from tkinter import messagebox, font
import cv2
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import image_managers, sample_extraction, percent, tube, segmentacion_contorno as sc
from utils import EntryWithPlaceholder

CLUSTER_RESHAPE = 0.5
IMAGE_RESHAPE = 0.7
    

class gui():
    def __init__(self, master) -> None:
        self.myFont = font.Font(size=13)
        self.main_win = master
        # self.main_win.maxsize(1300, 500)
        self.btns_fr = Frame(self.main_win)
        self.cropped_img_fr = Frame(self.main_win)
        self.img_container_fr = Frame(self.main_win)
        self.img_container_canvas= Canvas(self.img_container_fr)
        self.canvas_fr = Frame(self.img_container_canvas)
        self.img_tree = None
        self.selected_images_indices = []
        self.org_img = None
        self.results_fr = Frame(self.main_win)
        self.scrollbar = Scrollbar(self.img_container_fr, orient=HORIZONTAL , command = self.img_container_canvas.xview)
        self.btns_fr.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=NW)
        # self.img_container_fr.grid(row=1, column=2, columnspan=2)
        self.cropped_img_fr.grid(row=1, column=1)
        self.results_fr.grid(row=2,column=1,sticky=S)
        self.img_container_canvas.grid()
        
        
        self.canvas_fr.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas_fr.bind('<Leave>', self._unbound_to_mousewheel)

        self.img_container_canvas.configure(xscrollcommand= self.scrollbar.set)
        self.scrollbar.grid(row = 1, column=0, sticky=EW)
        self.canvas_fr.grid(row=0, column=0, sticky=NS)
        #self.img_container_canvas.create_window((0,0), window=self.canvas_fr, anchor=NW)
        
        # self.canvas_fr.grid()

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
        self.btnUp = Button(self.btns_fr, text='up', width=20, command=self.up, cursor='arrow')
        self.btnUp['font'] = self.myFont
        # #boton para avanzar en las imagenes creadas con clusters
        self.btnDown = Button(self.btns_fr, text='down', width=20, command=self.down, cursor='arrow')
        self.btnDown['font'] = self.myFont

        self.btnUndo = Button(self.btns_fr, text='undo', width=20, command=self.undo, cursor='arrow')
        self.btnUndo['font'] = self.myFont

        self.btnContour = Button(self.btns_fr, text='Segmentar', width=20, command=self.segmentate, cursor='arrow')
        self.btnContour['font'] = self.myFont

    def _bound_to_mousewheel(self, event):
        self.img_container_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.img_container_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.img_container_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
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
            #parámetros para resize

            self.org_img = img
            self.img_tree = refactor_gui.ImageNode(None, img)
            
            self.update_screen()
                    
            if isinstance(img, np.ndarray):
                self.btn3D.grid(row=0, column=1)
                self.num_of_cluster.grid(row=0, column=2)
                self.btnSplit.grid(row=0, column=3)
                self.btnMerge.grid(row=0, column=4)
                self.btnSub.grid(row=0, column=5)
                self.btnUp.grid(row=1, column=2)
                self.btnDown.grid(row=1, column=3)
                self.btnUndo.grid(row=1,column=0)
                self.btnContour.grid(row = 1, column = 4)
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
        self.img_container_fr.grid(row=1, column=2, columnspan=2)
    
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

            widgetP = Label(canvas, text=str(percent.percent(image)), fg='white', bg='black')
            widgetP.grid(row = 1,column=0 )

            widgetC = Label(canvas, text=str(percent.contour(image)), fg='white', bg='black')
            widgetC.grid(row = 2,column=0 )

    def update_screen(self):
        self.clean_win()
        # Imagen del nodo actual
        img = self.img_tree.image
        self.selected_images_indices = []

        # Set image for cropped image frame
        canva = Canvas(self.cropped_img_fr, width=img.shape[1], height=img.shape[0])
        fix_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _ = self.add_img_to_canvas(canva, fix_img)
        canva.grid(row=1, column=1)

        img_row_shape = 2
        i = 0
        for child in self.img_tree.childs:
            child_img = cv2.resize(child.image, (int(child.image.shape[1]*CLUSTER_RESHAPE), int(child.image.shape[0]*CLUSTER_RESHAPE)))
            child_img = cv2.cvtColor(child_img, cv2.COLOR_BGR2RGB)
            canva = Canvas(self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0])
            label = self.add_img_to_canvas(canva, child_img)
            label.bind('<ButtonPress-1>', lambda event, image=child.image, key=i, canvas=canva: self.click(image, key, canvas))
            canva.grid(row=1+i%img_row_shape, column=i//img_row_shape)
            i+=1
        
        try:
            self.canvas_fr.configure(scrollregion= self.img_container_canvas.bbox('all'))
        except:
            pass
        # self.img_container_canvas.bind('<Configure>', lambda e: self.img_container_canvas.configure(scrollregion= self.img_container_canvas.bbox('all')))
        # # self.canvas_fr = Frame(self.img_container_canvas)
        # self.img_container_canvas.create_window((0,0), window=self.canvas_fr, anchor=NW)
        # self.canvas_fr.grid()

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

    

win = Tk()
win.title("Cuantificador geologico")
win.iconbitmap("icon.ico")
win.config(cursor='plus')
gg = gui(win)        
win.mainloop()