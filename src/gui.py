import csv
from typing import Any, List
import image_tree
import tkinter as tk
import tkinter.font as tk_font
import numpy as np
import cv2
from PIL import Image, ImageTk
import image_managers, percent, tube, shape_detection as sc
from sample_extraction import SampleExtractor, cut_image_from_vertex, resize_unwrapping
from utils import EntryWithPlaceholder, createButtonWithHover, generate_zip, get_file_filepath, get_path, get_results_filepath

CLUSTER_RESHAPE = 0.7
ROOT = tk.Tk()
SCREEN_WIDTH = ROOT.winfo_screenwidth()
SCREEN_HEIGHT = ROOT.winfo_screenheight()
ARROW_LEFT = tk.PhotoImage(file="left_arrow.png")
ARROW_RIGHT = tk.PhotoImage(file="right_arrow.png")
    
class GUI(object):
    """
    The GUI class holds the behaviour of the graphic user interface
    of the geology cuantifier. It allows the user to interact with
    the diferent scripts developed for the processing and quanitification
    of rock samples.
    """
    def __init__(self, root: tk.Tk) -> None:
        """
        Constructor of the class. Instantiates class parameters related
        to both the workflow of the app and the elements of the interface.
        """

        # --- workflow parameters ---
        self.org_img = None
        self.img_tree = None
        self.selected_images_indices = []
        self.main_win = root
        self.main_win.bind("<1>", self.focus_win)
        self.key_pressed = ""
        self.clicked_pos = (0,0)
        # --- interface parameters ---
        
        # -- fonts -- 
        self.my_font = tk_font.Font(size=14)
        self.title_font = tk_font.Font(size=20)
        self.data_font = tk_font.Font(size=16)
        self.section_font = tk_font.Font(size=10)
        
        # -- frames --
        self.btns_fr = tk.Frame(self.main_win)
        self.btns_fr.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=tk.NW)

        self.file_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.file_fr.grid(row = 0, column= 0, sticky=tk.N)
        self.command_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.crop_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.size_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.size_sub_fr = tk.Frame(self.size_fr)
        self.color_seg_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.shape_seg_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.image_tools_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.gen_results_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)
        self.navigate_fr = tk.Frame(self.btns_fr, highlightbackground="light gray", highlightthickness=1)

        for i in range(6): self.btns_fr.columnconfigure(i, weight=1)

        self.img_container_fr = tk.Frame(self.main_win)
        
        self.img_container_canvas= tk.Canvas(self.img_container_fr)

        self.canvas_fr = tk.Frame(self.img_container_canvas)

        self.principal_fr = tk.Frame(self.main_win)
        self.principal_fr.grid(row=1, column=1)
        
        self.results_fr = tk.Frame(self.canvas_fr)

        # -- buttons --
        btn_img_name = 'Seleccionar imagen'
        btn_img_description = 'Permite abrir una imagen desde su PC.'
        self.btn_img, self.hover_img = createButtonWithHover(self.file_fr, btn_img_name, self.select_img, self.my_font, btn_img_description)
        self.btn_img.grid(row=0, column=0, padx=5, pady=5)

        btn_save_img_name = 'Recortar'
        btn_save_img_description = 'Recorta la imagen encerrada en el rectangulo que se ve en pantalla.'
        self.btn_save_img, self.hover_save_img = createButtonWithHover(self.command_fr, btn_save_img_name, self.save_image, self.my_font, btn_save_img_description)

        btn_reset_img_name = 'Restablecer'
        btn_reset_img_description = 'Reestablece la posición de los puntos usados para recortar la imagen.'
        self.btn_reset_img, self.hover_reset_img = createButtonWithHover(self.command_fr, btn_reset_img_name, self.reset_image, self.my_font, btn_reset_img_description)

        btn_panoramic_name = 'Modo panorámico'
        btn_panoramic_description = 'Es necesario posicionar 4 puntos para realizar un recorte sin ajuste de perspectiva.'
        self.btn_panoramic, self.hover_panoramic = createButtonWithHover(self.crop_fr, btn_panoramic_name, self.to_panoramic, self.my_font, btn_panoramic_description)

        btn_unwrapping_name = 'Modo unwrapping'
        btn_unwrapping_description = 'Es necesario posicionar 6 puntos para realizar un recorte con ajuste de perspectiva.'
        self.btn_unwrapping, self.hover_unwrapping = createButtonWithHover(self.crop_fr, btn_unwrapping_name, self.to_unwrapping, self.my_font, btn_unwrapping_description)
        
        btn_height_name = 'Altura'
        btn_height_description = 'Permite guardar la altura (en cm) de la roca introdujida.'
        self.btn_height, self.hover_height = createButtonWithHover(self.size_sub_fr, btn_height_name, self.set_height, self.my_font, btn_height_description)

        btn_save_name = 'Guardar'
        btn_save_description = 'Guarda la imagen actual junto con las imágenes obtenidas al segmentar por color.'
        self.btn_save, self.hover_save = createButtonWithHover(self.file_fr, btn_save_name, self.save, self.my_font, btn_save_description)
       
        btn_split_name = 'Separar'
        btn_split_description = 'Segmenta la imagen por colores, generando una cantidad de imagenes igual al número ingresado.'
        self.btn_split, self.hover_split = createButtonWithHover(self.color_seg_fr, btn_split_name, self.split, self.my_font, btn_split_description)

        btn_merge_name = 'Combinar'
        btn_merge_description = 'Permite combinar 2 o más imagenes en una sola.'
        self.btn_merge, self.hover_merge = createButtonWithHover(self.color_seg_fr, btn_merge_name, self.merge, self.my_font, btn_merge_description)
        
        btn_sub_name = 'Eliminar'
        btn_sub_description = 'Permite eliminar 1 o más imagenes, también se refleja en la imagen original.'
        self.btn_sub, self.hover_sub = createButtonWithHover(self.color_seg_fr, btn_sub_name, self.delete, self.my_font, btn_sub_description)

        btn_outline_name = 'Perfilar'
        btn_outline_description = 'Perfila la imagen seleccionada.'
        self.btn_outline, self.hover_outline = createButtonWithHover(self.shape_seg_fr, btn_outline_name, self.outline, self.my_font, btn_outline_description)

        btn_segmentate_name = 'Segmentar'
        btn_segmentate_description = 'Calcula resultados utilizando como base la imagen seleccionada.'
        self.btn_segmentate, self.hover_segmentate = createButtonWithHover(self.shape_seg_fr, btn_segmentate_name, self.segmentate, self.my_font, btn_segmentate_description)

        btn_update_name = 'Actualizar'
        btn_update_description = 'Actualiza la pantalla, ajustando el tamaño de las imágenes presentes en ella.'
        self.btn_update, self.hover_update = createButtonWithHover(self.image_tools_fr, btn_update_name, self.update_screen, self.my_font, btn_update_description)
 
        btn_undo_name = 'Deshacer'
        btn_undo_description = 'Deshace todos los cambios hechos sobre la imagen.'
        self.btn_undo, self.hover_undo = createButtonWithHover(self.image_tools_fr, btn_undo_name, self.undo, self.my_font, btn_undo_description)

        btn_3d_name = '3D'
        btn_3d_description = 'Permite visualizar en 3D la imagen que se encuentra en la pantalla.'
        self.btn_3d, self.hover_3d = createButtonWithHover(self.gen_results_fr, btn_3d_name, self.plot_3d, self.my_font, btn_3d_description)
       
        btn_analyze_name = 'Analizar'
        btn_analyze_description = 'Permite analizar la imagen seleccionada, calculando las estadisticas presentes en el programa.'
        self.btn_analyze, self.hover_analyze = createButtonWithHover(self.gen_results_fr, btn_analyze_name, self.analyze, self.my_font, btn_analyze_description)

        btn_up_name = 'Subir'
        btn_up_description = 'Permite acceder a la imagen que se tenia anteriormente.'
        self.btn_up, self.hover_up = createButtonWithHover(self.navigate_fr, btn_up_name, self.up, self.my_font, btn_up_description, image=ARROW_LEFT)
        
        btn_down_name = 'Bajar'
        btn_down_description = 'Permite cambiar la imagen actual por la imagen seleccionada.'
        self.btn_down, self.hover_down = createButtonWithHover(self.navigate_fr, btn_down_name, self.down, self.my_font, btn_down_description,image=ARROW_RIGHT)

        # -- entries --
        self.total_clusters = EntryWithPlaceholder(self.color_seg_fr, "Número de clusters", 'gray')
        self.total_clusters.config(borderwidth=2)
        self.total_clusters['font'] = self.my_font

        self.entry_height_cm = EntryWithPlaceholder(self.size_sub_fr, "Altura recorte (cm)", 'gray')
        self.entry_height_cm['font'] = self.my_font

        # -- labels --
        self.file_fr_lbl = tk.Label(self.file_fr, text = "Archivos", font= self.section_font)
        self.file_fr_lbl.grid(column= 0)
        self.command_fr_lbl = tk.Label(self.command_fr, text = "Comandos",  font= self.section_font)
        self.crop_fr_lbl = tk.Label(self.crop_fr, text = "Modo de\n recorte", font= self.section_font)
        self.size_fr_lbl = tk.Label(self.size_fr, text = "Tamaño", font= self.section_font)
        self.color_seg_lb = tk.Label(self.color_seg_fr, text = "Segmentación color", font= self.section_font)
        self.shape_seg_lb = tk.Label(self.shape_seg_fr, text = "Segmentación \n forma", font= self.section_font)
        self.image_tools_lb = tk.Label(self.image_tools_fr, text = "Modificar imagen", font= self.section_font)
        self.gen_results_lb = tk.Label(self.gen_results_fr, text = "Generación \n resultados", font= self.section_font)
        self.navigate_lb = tk.Label(self.navigate_fr, text = "Navegar", font= self.section_font)


        # -- extras --
        self.set_up_scrollbar()
        self.btn_fr_size = 200
        self.segmentation = False
        self.height_cm = 0
        self.mode = 'p'

    
    def set_height(self):
        try:
            self.height_cm = int(self.entry_height_cm.get())
        except:
            tk.messagebox.showwarning("Error", message="Por favor ingresa un número.")
            return


    def focus_win(self, event):
        if not isinstance( event.widget, tk.Entry):
            self.main_win.focus()

    def set_up_scrollbar(self):
        """
        Sets up the scrollbar of the gui, instantiating tk.Scrollbar
        and positioning it.
        """
        self.scrollbar = tk.Scrollbar(self.img_container_fr, orient=tk.HORIZONTAL , command = self.img_container_canvas.xview)

        self.canvas_fr.bind(
            "<Configure>",
            lambda _: self.img_container_canvas.configure(
                scrollregion=self.img_container_canvas.bbox("all")
            )
        )

        self.img_container_canvas.create_window((0,0), window=self.canvas_fr, anchor="center")

        self.main_win.columnconfigure(2, weight=1)
        self.main_win.rowconfigure(1, weight=1)

        self.img_container_fr.columnconfigure(0, weight=1)
        self.img_container_fr.rowconfigure(0, weight=1)
        self.img_container_canvas.configure(xscrollcommand=self.scrollbar.set)

        self.img_container_canvas.grid()
        
        
        self.canvas_fr.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas_fr.bind('<Leave>', self._unbound_to_mousewheel)

        self.img_container_canvas.configure(xscrollcommand= self.scrollbar.set)
        self.scrollbar.grid(row = 1, column=0, sticky=tk.N+tk.EW)
        self.img_container_canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

    def _bound_to_mousewheel(self, event):
        """
       Private method, handles the binding of the mouse wheel
        """
        self.img_container_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """
        Private method, handles the unbinding of the mouse wheel
        """
        self.img_container_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """
        Private method, handles scrollbar mouse wheel scrolling
        """
        self.img_container_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def split(self) -> None:
        """
        Splits the current image by doing KMeans clustering on it. The number of clusters
        is given by the user by filling the 'total_clusters' entry.
        """
        try :
            n_childs = int(self.total_clusters.get())
        except:
            tk.messagebox.showwarning("Error", message="Por favor ingresa un número.")
            return
        selected_imgs = len(self.selected_images_indices)
        
        if selected_imgs > 1:
            tk.messagebox.showwarning("Error", message="Por favor, seleccione solo una imagen.")
            return
        
        if selected_imgs == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        
        self.img_tree.split(n_childs=n_childs)
        self.segmentation = False
        self.update_screen()
        self.selected_images_indices=[]
    
    def click_check(self, event):
        self.sample_extractor.check_circle_movement(event.x, event.y)
    
    def click_pos(self, event):
        self.sample_extractor.move_vertex(event.x, event.y)
        photo_img = cv2.cvtColor(self.sample_extractor.get_image(), cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        self.label_extractor.configure(image=img_for_label)
        self.label_extractor.image = img_for_label
        self.label_extractor.grid(row=0, column=0, padx=10, pady=10)

    def choose_cut_method(self):
        if self.mode == 'p':
            return cut_image_from_vertex(self.org_img, self.sample_extractor)
        elif self.mode == 'w':
            return resize_unwrapping(self.org_img, self.sample_extractor)
    
    def to_unwrapping(self):
        self.crop(self.org_img, 6)  
        self.mode = 'w'

    def to_panoramic(self):
        self.crop(self.org_img, 4)
        self.mode = 'p'

    def save_image(self):
        self.org_img = self.choose_cut_method()
        self.main_win.unbind('<Key>')
        self.un_measures()
        self.show_img()
        for wget in self.command_fr.winfo_children():
            wget.grid_forget()
        for wget in self.crop_fr.winfo_children():
            wget.grid_forget()
        for wget in self.size_fr.winfo_children():
            wget.grid_forget()
        self.command_fr.grid_forget()
        self.crop_fr.grid_forget()    
        self.size_fr.grid_forget()                  

    def reset_image(self):
        self.sample_extractor.reset_vertexes_pos()
        self.sample_extractor.refresh_image()
        photo_img = cv2.cvtColor(self.sample_extractor.get_image(), cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        self.label_extractor.configure(image=img_for_label)
        self.label_extractor.image = img_for_label
        self.label_extractor.grid(row=0, column=0, padx=10, pady=10)

    def key_press(self, event):
        if event.char == "s":
            self.save_image()
        elif event.char == 'p':
            self.to_panoramic()
        elif event.char == "w":
            self.to_unwrapping()
        elif event.char == "r":
            self.reset_image()
    
    def release_click(self, event):
        self.sample_extractor.refresh_image()

    def crop(self, image, n=4):
        self.sample_extractor = SampleExtractor(self._resize_img(image), n)
        #se ingresa en un canvas
        canvas_extractor = tk.Canvas(self.principal_fr)
        self.label_extractor = self.add_img_to_canvas(canvas_extractor, self.sample_extractor.get_image())
        self.label_extractor.bind('<1>', self.click_check)
        self.label_extractor.bind('<B1-Motion>',self.click_pos)
        self.label_extractor.bind('<ButtonRelease-1>', self.release_click)
        self.main_win.bind('<Key>',self.key_press)
        canvas_extractor.grid(row=0, column=0)

    def measures(self):
        self.size_fr.grid(row=0, column=4, sticky=tk.N)
        self.size_sub_fr.grid(row=0, column=0)
        self.entry_height_cm.grid(row=0, column=0)
        self.btn_height.grid(row=0, column=1)
        self.size_fr_lbl.grid(row=1, column=0)

    def un_measures(self):
        
        self.entry_height_cm.grid_forget()
        self.btn_height.grid_forget()
        self.size_fr_lbl.grid_forget()
        self.size_fr.grid_forget()
        self.size_sub_fr.grid_forget()

    def select_img(self):
        try:
            img = image_managers.load_image_from_window()
            #set max resolution
            #TODO: Move to another module
            resize_height = SCREEN_HEIGHT
            resize_width = SCREEN_WIDTH
            resize_img = img
            if img.shape[0] > resize_height:
                # Adjust image to the define height
                resize_img = cv2.resize(img, ((int(img.shape[1] * resize_height / img.shape[0])), resize_height))
                # If its new width exceed the define width
            if resize_img.shape[1] > resize_width:
                # Adjust image to the define width
                resize_img = cv2.resize(resize_img, (resize_width, int(resize_img.shape[0] * resize_width / resize_img.shape[1])))

            self.org_img = resize_img
            self.clean_principal_frame()
            self.clean_canvas_frame()
            self.clean_btns()
            self.crop(resize_img)

            self.measures()

            # -- File managment
            self.file_fr.grid(row=0, column=0, sticky=tk.N)
            self.btn_img.grid(row=0, column=0, padx=5, pady=5)
            self.file_fr_lbl.grid(column= 0)
            # -- commands --
            self.command_fr.grid(row=0, column=1, sticky=tk.N)
            self.btn_save_img.grid(row=0, column=0, padx=5, pady=5)
            self.btn_reset_img.grid(row=1, column=0, padx=5, pady=5)
            self.command_fr_lbl.grid(column=0, padx=5, pady=5)
            # -- crop types --
            self.crop_fr.grid(row = 0, column= 2, sticky=tk.N)
            self.btn_panoramic.grid(row=0, column=0,padx=5, pady=5)
            self.btn_unwrapping.grid(row=1, column=0, padx=5, pady=5)
            self.crop_fr_lbl.grid(column=0,padx=5, pady=5)
            

            self.segmentation = False
            self.mode = 'p'
        except:
           pass

    def show_img(self) -> None:
        """
        This method is called when a new image is uploaded. 
        """
        # self.clean_frames()
        self.img_tree = image_tree.ImageNode(None, self.org_img)
        self.segmentation = False
        self.update_screen()
                
        # Set buttons positions
        self.create_btns()

    def clean_btns(self) -> None:
        for wget in self.file_fr.winfo_children():
            wget.grid_forget()
        self.file_fr.grid_forget()
        for wget in self.color_seg_fr.winfo_children():
            wget.grid_forget()
        self.color_seg_fr.grid_forget()
        for wget in self.shape_seg_fr.winfo_children():
            wget.grid_forget()
        self.shape_seg_fr.grid_forget()
        for wget in self.image_tools_fr.winfo_children():
            wget.grid_forget()
        self.image_tools_fr.grid_forget()
        for wget in self.gen_results_fr.winfo_children():
            wget.grid_forget()
        self.gen_results_fr.grid_forget()
        for wget in self.navigate_fr.winfo_children():
            wget.grid_forget()
        self.navigate_fr.grid_forget()


    def create_btns(self) -> None:
        
        # -- files --
        self.btn_save.grid(row=0, column=1, padx=5, pady=5)
        self.file_fr_lbl.grid(column= 0, padx=5, pady=5)

        # -- Color Segmentation --
        self.color_seg_fr.grid(row=0, column=1, sticky=tk.N)
        self.total_clusters.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=5)
        self.btn_split.grid(row=0, column=1, padx=5, pady=5)
        self.btn_merge.grid(row=1, column=0, padx=5, pady=5)
        self.btn_sub.grid(row=1, column=1, padx=5, pady=5)
        self.color_seg_lb.grid(padx=5, pady=5)

        # -- Shape Segmentation --
        self.shape_seg_fr.grid(row=0, column=2, sticky=tk.N)
        self.btn_outline.grid(row=0, column=0, padx=5, pady=5)
        self.btn_segmentate.grid(row=1, column=0, padx=5, pady=5)
        self.shape_seg_lb.grid(column=0, padx=5, pady=5)

        # -- Image Tools
        self.image_tools_fr.grid(row=0, column=3, sticky=tk.N)
        self.btn_update.grid(row=0, column=0, padx=5, pady=5)
        self.btn_undo.grid(row=1, column=0, padx=5, pady=5)
        self.image_tools_lb.grid(column=0, padx=5, pady=5)

        # -- Results generation --
        self.gen_results_fr.grid(row=0, column=4, sticky=tk.N)
        self.btn_3d.grid(row=0, column=0, padx=5, pady=5)
        self.btn_analyze.grid(row=0, column=0, padx=5, pady=5)
        self.gen_results_lb.grid(column=0, padx=5, pady=5)

        # -- Navigate --
        self.navigate_fr.grid(row=1, column=0, sticky=tk.N)
        self.btn_up.grid(row=0, column=0, padx=5, pady=5)
        self.btn_down.grid(row=0, column=1, padx=5, pady=5)
        self.navigate_lb.grid(column=0, padx=5, pady=5)


    def clean_principal_frame(self) -> None:
        """
        Destroy the principal frame and start a new one.
        """
        for wget in self.principal_fr.winfo_children():
            wget.destroy()
        self.principal_fr.destroy()
        self.principal_fr = tk.Frame(self.main_win)
        self.principal_fr.grid(row=1, column=1)
    
    def clean_canvas_frame(self) -> None:
        """
        Destroy every tkinter instance inside the canvas frame
        and start new one.
        """
        for wget in self.results_fr.winfo_children():
            wget.destroy()

        for wget in self.canvas_fr.winfo_children():
            wget.destroy()
        self.results_fr = tk.Frame(self.canvas_fr)
        self.img_container_fr.grid(row=1, column=2, sticky=tk.N+tk.E+tk.W+tk.S)
    
    def add_img_to_canvas(self, canvas: tk.Canvas, img: cv2.Mat) -> None:
        """
        Adds an image to the canvas.
        """
        photo_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        label_img = tk.Label(canvas, image=img_for_label)
        label_img.image = img_for_label
        label_img.grid(row=0, column=0, padx=10, pady=10)
        return label_img
        
    def click(self, image: cv2.Mat, key: Any, canvas: tk.Canvas) -> None:
        """
        Handles the clicks on screen, unselecting previous images if needed
        or selecting new ones.
        """
        if key in self.selected_images_indices:
            self.selected_images_indices.remove(key)
            canvas.configure(bg='white')
            for widget in canvas.winfo_children():
                if widget.cget("text"):
                    widget.destroy()
        else:
            self.selected_images_indices.append(key)
            canvas.configure(bg='red')

            color_percent = percent.percent(image)
            widgetP = tk.Label(canvas, text=f"Porcentaje de pixeles: {color_percent}%", fg='white', bg='black')
            widgetP.grid(row = 1,column=0 )

    def _resize_img(self, img):
        """
        Resize the image acording to the actual window size of the aplication.
        """
        # Get actual window size
        win_height = self.main_win.winfo_height()
        win_width = self.main_win.winfo_width()
        padding_size = 10
        # Define the desire height and width of the image
        resize_height = int((win_height - self.btn_fr_size - padding_size) * 1 // 2)
        resize_width = int((win_width - padding_size / 2) * 1 // 3)

        # If the larger size of the image is its height (type TUBE)
        if img.shape[0] > img.shape[1]:
            # Adjust image to the define height
            resize_img = cv2.resize(img, ((int(img.shape[1] * resize_height / img.shape[0])), resize_height))
            # If its new width exceed the define width
            if resize_img.shape[1] > resize_width:
                # Adjust image to the define width
                resize_img = cv2.resize(resize_img, (resize_width, int(resize_img.shape[0] * resize_width / resize_img.shape[1])))
        # If the larger size of the image is its width (type PANORAMIC)
        else:
            # Adjust image to the define width
            resize_img = cv2.resize(img, (resize_width, int(img.shape[0] * resize_width / img.shape[1])))
            # If its new height exceed the define height
            if resize_img.shape[0] > resize_height:
                # Adjust image to the define height
                resize_img = cv2.resize(resize_img,  ((int(resize_img.shape[1] * resize_height / resize_img.shape[0])), resize_height))

        return resize_img

    def update_screen(self) -> None:
        """
        Updates the screen, this method is called right after
        the user interacts with the current image.
        """
        self.clean_principal_frame()

        img = self._resize_img(self.img_tree.image) # image at the current node of the image_tree
        self.selected_images_indices = [] # resets selected images

        if self.segmentation:
            principal_image = self.img_tree.image
            principal_image_res = self._resize_img(principal_image)
            principal_canva = tk.Canvas(self.principal_fr, width=principal_image_res.shape[1], height=principal_image_res.shape[0])
            self.add_img_to_canvas(principal_canva, principal_image_res)
            principal_canva.grid(row=0, column=0)

            self.segmentated = self._resize_img(self.segmentated)
            canva = tk.Canvas(self.principal_fr, width=self.segmentated.shape[1], height=self.segmentated.shape[0])
            self.add_img_to_canvas(canva, self.segmentated)
            if self.segmentated.shape[0] > self.segmentated.shape[1]:
                canva.grid(row=0, column=1)
            else:
                canva.grid(row=1, column=0)
            
        else:
            self.clean_canvas_frame()
            # Set image for cropped image frame
            canva = tk.Canvas(self.principal_fr, width=img.shape[1], height=img.shape[0])
            _ = self.add_img_to_canvas(canva, img)
            canva.grid(row=0, column=0)

            # draws image node childs
            img_row_shape = 2
            i = 0
            for child in self.img_tree.childs:
                child_img = self._resize_img(child.image)
                child_img = cv2.resize(child.image, (int(child_img.shape[1]*CLUSTER_RESHAPE), int(child_img.shape[0]*CLUSTER_RESHAPE)))
                canva = tk.Canvas(self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0])
                label = self.add_img_to_canvas(canva, child_img)
                label.bind('<ButtonPress-1>', lambda event, image=child.image, key=i, canvas=canva: self.click(image, key, canvas))
                canva.grid(row=i%img_row_shape, column=i//img_row_shape)
                i+=1

    def merge(self) -> None:
        """
        This method merges 2 or more clusters, updating the image tree.
        """
        if len(self.selected_images_indices) < 2:
            tk.messagebox.showwarning("Error", message="Por favor, seleccione 2 o más imagenes.")
            return
        self.img_tree.merge(self.selected_images_indices)
        self.segmentation = False
        self.update_screen()
        self.selected_images_indices=[]

    def delete(self) -> None:
        """
        This method deletes at least 1 cluster, updating the image tree.
        """
        if len(self.selected_images_indices) == 0:
            tk.messagebox.showwarning("Error", message="Por favor, seleccione al menos una imagen.")
            return
        self.img_tree.delete(self.selected_images_indices)
        self.segmentation = False
        self.update_screen()
        self.selected_images_indices=[]

    def plot_3d(self) -> None:
        """
        This method plots the image of the current node of the image tree
        in a 3D model of a cilinder.
        """
        # tk.messagebox.showinfo("Proximamente", message="Esta funcionalidad estará disponible proximamente.")

        img = self.img_tree.image
        # # Use the loaded img to fill a 3D tube surface.
        tube.fill_tube(img)
        
    def undo(self) -> None:
        """
        Resets the image tree back to it's original form.
        """
        self.img_tree = image_tree.ImageNode(None,self.org_img)
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def down(self) -> None:
        """
        Travels one level downwards in the image tree, this means that the GUI
        will show a cluster as a main image and the user will be able to
        call functions on it.
        """
        if len(self.selected_images_indices) != 1:
            tk.messagebox.showwarning("Error", message="Por favor, seleccione una imagen.")
            return
        self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def up(self) -> None:
        """
        Travels one level upwards in the image tree, updates the GUI showing all the data
        related to the parent of the current node.
        """
        if self.img_tree.parent == None:
            tk.messagebox.showwarning("Error", message="Esta es la imagen original.")
            return
        self.img_tree = self.img_tree.parent
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()
    
    def analyze(self) -> None:
        tk.messagebox.showwarning("Proximamente", message="Esta funcionalidad estara disponible proximamente.")

    def outline(self) -> None:
        tk.messagebox.showwarning("Proximamente", message="Esta funcionalidad estara disponible proximamente.")

    def segmentate(self) -> None:
        """
        This method is in charge of the body detection at a cluster
        """
        if len(self.selected_images_indices) > 1:
            tk.messagebox.showwarning("Error", message="Por favor, seleccione solo una imagen.")
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        
        self.clean_principal_frame()
        self.clean_canvas_frame()

        self.selected_images_indices = []
        self.segmentation = True
        
        self.contour = sc.contour_segmentation(self.img_tree.image) 
        sc.contour_agrupation(self.contour)
        self.segmentated = sc.cluster_segmentation(self.img_tree.image,self.contour)

        self.update_screen()

        results = sc.generate_results(self.contour, self.height_cm/self.segmentated.shape[0])
        self.fill_table(results)

    def aggregate(self, results) -> List:
        agg_results = []
        color_count = []
        # Results list initialization
        for i in range(len(sc.COLORS)):
            agg_results.append([])
            color_count.append(0)
            for _ in sc.STATISTICS:
                agg_results[i].append(0)
        for res in results:
            color_count[res[0]] += 1
            for i in range(len(sc.STATISTICS)):
                # i is the statistic to aggregate
                # i+1 is the position of the statistic
                # in the res list
                agg_results[res[0]][i] += res[i+1]
        
        for i in range(len(agg_results)):
            for j in range(len(sc.STATISTICS)):
                if color_count[i] != 0:
                    agg_results[i][j] /= color_count[i]
                    agg_results[i][j] = np.round(agg_results[i][j], 2)
        return agg_results

    def create_label(self, name, row, col):
        label = tk.Label(self.results_fr, text=name, highlightthickness=1, highlightbackground="black")
        label.grid(row=row, column=col, sticky=tk.N+tk.S+tk.E+tk.W)
        return label

    def fill_table(self, results) -> None:
        """
        This method fills and shows a table at the GUI.
        The data is given as an input.
        """
        aggregated_results = self.aggregate(results)
        self.results_fr.grid(row=0,column=0)
        self.img_container_canvas.xview('moveto', 0)
        self.create_label("Color", 0, 0)
        self.create_label("MIneral", 0, 1)
        for i in range(len(sc.STATISTICS)):
            self.create_label(sc.STATISTICS[i], 0, i+2)
        
        for row_num in range(len(aggregated_results)):
            (b, g, r) = sc.COLORS[row_num]
            color = '#%02x%02x%02x' % (r, g, b)
            label_color = self.create_label("", row_num+1, 0)
            label_color.config(bg=color, width=1, height=1, justify=tk.CENTER)
            
            name = EntryWithPlaceholder(self.results_fr, f"Mineral {row_num}")
            name.config(highlightthickness=1, highlightbackground="black")
            name['font'] = self.my_font
            name.grid(row=row_num+1, column=1, sticky=tk.W+tk.E)

            for col_num in range(len(sc.STATISTICS)):
                self.create_label(aggregated_results[row_num][col_num], row_num+1, col_num+2)

        self.btnExport = tk.Button(self.results_fr, text="Descargar", width=15, command=lambda : self.table_to_csv(results) , cursor='arrow')
        self.btnExport['font'] = self.my_font
        self.btnExport.grid(row=len(aggregated_results) + 1, column=len(sc.STATISTICS) // 2 + 1)
    
    def table_to_csv(self, results) -> None:
        """
        This method takes the data from a table at the GUI
        and generates a csv with it.
        """
        # Get user location of results
        filepath = get_results_filepath()
        if not filepath:
            return
        
        # Get the names the user set
        names = []
        wgets = self.results_fr.winfo_children()[:-1]
        entrys = [wgets[i+1] for i in range(len(sc.STATISTICS)+2, len(wgets), len(sc.STATISTICS)+2)]
        for entry in entrys:
            names.append(entry.get())

        header_row = ["Nombre Mineral", "ID imagen", *sc.STATISTICS]
        # images = []
        with open(f'{filepath}_data.csv', 'w', newline='') as f:
            wrtr = csv.writer(f, delimiter=',')
            wrtr.writerow(header_row)
            for i in range(len(results)):
                row = []
                row.append(names[results[i][0]])
                # images.append(contour[i].img)
                row.append(str(i))
                for j in range(len(sc.STATISTICS)):
                    row.append(results[i][j+1])
                wrtr.writerow(row)
        images = sc.image_agrupation(self.org_img,self.contour,3)
        generate_zip(f'{filepath}_images', images)
        tk.messagebox.showinfo("Guardado", message="Los resultados se han guardado correctamente")
    
    def save(self) -> None:
        """
        This method saves both the current image and it's clusters if they exist.
        """
        files = [self.img_tree.image]
        
        for child in self.img_tree.childs:
            files.append(child.image)
        

        filepath = get_file_filepath()
        if not filepath:
            return

        generate_zip(filepath, files)
        tk.messagebox.showinfo("Guardado", message="Las imagenes se han guardado correctamente")


ROOT.title("Cuantificador geologico")
ROOT.wm_iconbitmap(get_path('icon.ico'))
ROOT.config(cursor='plus')
# Get user screen size

# Open window smaller than user screen
ROOT.geometry(f"{SCREEN_WIDTH * 19 // 20}x{SCREEN_HEIGHT * 17 // 20}+0+0")
# Set min and max window size to avoid incorrect displays
ROOT.minsize(SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT * 2 // 3)
ROOT.maxsize(SCREEN_WIDTH, SCREEN_HEIGHT)
gg = GUI(ROOT)        
ROOT.mainloop()