import csv
import image_tree
import tkinter
import tkinter.font as tk_font
import numpy as np
import cv2
import image_managers, percent, tube, shape_detection as sc
import sv_ttk
from tkinter import ttk
import tkinter.messagebox

from PIL import Image, ImageTk
from sample_extraction import ExtractorModeEnum, SampleExtractor
from utils import PlaceholderEntry, generate_zip, get_file_filepath, get_path, get_results_filepath
from typing import Any, List

CLUSTER_RESHAPE = 0.7
ROOT = tkinter.Tk()
SCREEN_WIDTH = ROOT.winfo_screenwidth()
SCREEN_HEIGHT = ROOT.winfo_screenheight()
    
class GUI(object):
    """
    The GUI class holds the behaviour of the graphic user interface
    of the geology cuantifier. It allows the user to interact with
    the diferent scripts developed for the processing and quanitification
    of rock samples.
    """
    def __init__(self, root: tkinter.Tk) -> None:
        """
        Constructor of the class. Instantiates class parameters related
        to both the workflow of the app and the elements of the interface.
        """

        # --- workflow parameters ---
        self.org_img = None
        self.clone_img = None
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
        
        # -- frames --
        self.btns_fr = ttk.Frame(self.main_win, style='Card.TFrame', padding=(5, 6, 7, 8))
        self.btns_fr.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=tkinter.NW)
        for i in range(6): self.btns_fr.columnconfigure(i, weight=1)

        self.img_container_fr = ttk.Frame(self.main_win, style='Card.TFrame', padding=(5, 6, 7, 8))
        
        self.img_container_canvas= tkinter.Canvas(self.img_container_fr)

        self.canvas_fr = ttk.Frame(self.img_container_canvas, style='Card.TFrame', padding=(5, 6, 7, 8))

        self.principal_fr = ttk.Frame(self.main_win, style='Card.TFrame', padding=(5, 6, 7, 8))
        self.principal_fr.grid(row=1, column=1)
        
        self.results_fr = ttk.Frame(self.canvas_fr, style='Card.TFrame', padding=(5, 6, 7, 8))

        # -- buttons --
        self.btn_img = ttk.Button(self.btns_fr, style="Accent.TButton" ,text='Seleccionar imagen', width=20, command=self.select_img, cursor='arrow')
        self.btn_img.grid(row=0, column=0, padx=5, pady=5)

        self.btn_panoramic = ttk.Button(self.btns_fr, text='Modo panorámico', width=20, command=self.to_panoramic, cursor='arrow')

        self.btn_unwrapping = ttk.Button(self.btns_fr, text='Modo unwrapping', width=20, command=self.to_unwrapping, cursor='arrow')

        self.btn_rotateR = ttk.Button(self.btns_fr, text='Rotar imagen R', width=20, command=self.rotateR, cursor='arrow')

        self.btn_rotateL = ttk.Button(self.btns_fr, text='Rotar imagen L', width=20, command=self.rotateL, cursor='arrow')

        self.btn_save_img = ttk.Button(self.btns_fr, text='Guardar imagen', width=20, command=self.save_image, cursor='arrow')

        self.btn_3d = ttk.Button(self.btns_fr, text='3D', width=20, command=self.plot_3d, cursor='arrow')

        self.btn_split = ttk.Button(self.btns_fr, text='Separar', width=20, command=self.split, cursor='arrow')

        self.btn_merge = ttk.Button(self.btns_fr, text='Combinar', width=20, command=self.merge, cursor='arrow')
        
        self.btn_sub = ttk.Button(self.btns_fr, text='Eliminar', width=20, command=self.delete, cursor='arrow')
        
        self.btn_up = ttk.Button(self.btns_fr, text='Subir', width=20, command=self.up, cursor='arrow')
        
        self.btn_down = ttk.Button(self.btns_fr, text='Bajar', width=20, command=self.down, cursor='arrow')

        self.btn_undo = ttk.Button(self.btns_fr, text='Deshacer', width=20, command=self.undo, cursor='arrow')

        self.btn_save = ttk.Button(self.btns_fr, text='Guardar', width=20, command=self.save, cursor='arrow')

        self.btn_update = ttk.Button(self.btns_fr, text='Actualizar', width=20, command=self.update_screen, cursor='arrow')

        self.btn_analyze = ttk.Button(self.btns_fr, text='Analizar', width=20, command=self.analyze, cursor='arrow')

        self.btn_segmentate = ttk.Button(self.btns_fr, text='Segmentar', width=20, command=self.segmentate, cursor='arrow')

        self.btn_rotate = ttk.Button(self.btns_fr, text='Girar', width=20, command=self.rotate_image, cursor='arrow')

        self.btn_height = ttk.Button(self.btns_fr, text='Altura', width=20, command=self.set_height, cursor='arrow')

        # -- entries --
        self.total_clusters = PlaceholderEntry(self.btns_fr, "Número de clusters")
        self.entry_height_cm = PlaceholderEntry(self.btns_fr, "Altura recorte (cm)")

        # -- extras --
        self.set_up_scrollbar()
        self.btn_fr_size = 200
        self.segmentation = False
        self.height_cm = 0
        self.mode = 'p'
        self.grados = 0
        self.canvas_preview = tkinter.Canvas(self.principal_fr)
        self.prev_boolean = False

    def set_height(self):
        entry_val = self.entry_height_cm.get()
        if entry_val.isnumeric():
            self.height_cm = int(entry_val)

    def focus_win(self, event):
        if not isinstance( event.widget, ttk.Entry):
            self.main_win.focus()

    def set_up_scrollbar(self):
        """
        Sets up the scrollbar of the gui, instantiating ttk.Scrollbar
        and positioning it.
        """
        self.scrollbar = ttk.Scrollbar(self.img_container_fr, orient=tkinter.HORIZONTAL , command = self.img_container_canvas.xview)

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
        self.scrollbar.grid(row = 1, column=0, sticky=tkinter.N+tkinter.EW)
        self.img_container_canvas.grid(row=0, column=0, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

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
            tkinter.messagebox.showwarning("Error", message="Por favor ingresa un número.")
            return
        selected_imgs = len(self.selected_images_indices)
        
        if selected_imgs > 1:
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione solo una imagen.")
            return
        
        if selected_imgs == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        
        self.img_tree.split(n_childs=n_childs)
        self.segmentation = False
        self.update_screen()
        self.selected_images_indices=[]
    
    def click_check(self, event):
        self.sample_extractor.check_mov(event.x, event.y)
    
    def click_pos(self, event):
        self.sample_extractor.move_vertex(event.x, event.y)
        photo_img = cv2.cvtColor(self.sample_extractor.get_image(), cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        self.label_extractor.configure(image=img_for_label)
        self.label_extractor.image = img_for_label
        self.label_extractor.grid(row=0, column=0, padx=10, pady=10)

    def choose_cut_method(self, img = None):
        if not self.prev_boolean:
            img = self.org_img
        
        return self.sample_extractor.cut(img)
    
    def to_unwrapping(self):
        self.crop(self.org_img, ExtractorModeEnum.UNWRAPPER)  
        self.mode = 'w'

    def rotateR(self):
        # degree = cv2.getTrackbarPos('degree','Cuantificador geologico')
        image_center = tuple(np.array(self.clone_img.shape[1::-1]) / 2)
        self.grados-=0.2
        rotation_matrix = cv2.getRotationMatrix2D(image_center, angle=self.grados, scale=1)
        # rotated_image = cv2.warpAffine(self.org_img, rotation_matrix,(self.org_img.shape[1],self.org_img.shape[0]))
        self.org_img = cv2.warpAffine(self.clone_img, rotation_matrix,(self.clone_img.shape[1],self.clone_img.shape[0]))
        self.crop(self.org_img, ExtractorModeEnum.PANORAMIC)
    
    def rotateL(self):
        # degree = cv2.getTrackbarPos('degree','Frame')
        image_center = tuple(np.array(self.clone_img.shape[1::-1]) / 2)
        self.grados+=0.2
        rotation_matrix = cv2.getRotationMatrix2D(image_center, angle=self.grados, scale=1)
        # rotated_image = cv2.warpAffine(self.org_img, rotation_matrix,(self.org_img.shape[1],self.org_img.shape[0]))
        self.org_img = cv2.warpAffine(self.clone_img, rotation_matrix,(self.clone_img.shape[1],self.clone_img.shape[0]))
        self.crop(self.org_img, ExtractorModeEnum.PANORAMIC)

    def preview(self):
        if self.canvas_preview:
            self.canvas_preview.destroy()
        self.canvas_preview = tkinter.Canvas(self.principal_fr)
        self.prev_boolean = True
        copy_img = np.copy(self.org_img)
        copy_img = self.choose_cut_method(copy_img)
        self.label_extractor2 = self.add_img_to_canvas(self.canvas_preview, copy_img)
        self.canvas_preview.grid(row=0,column=1)

    def to_panoramic(self):
        self.crop(self.org_img, ExtractorModeEnum.PANORAMIC)
        self.mode = 'p'

    def save_image(self):
        self.prev_boolean = False
        self.org_img = self.choose_cut_method()
        self.main_win.unbind('<Key>')
        self.un_measures()
        self.show_img()
        self.btn_panoramic.grid_forget()
        self.btn_unwrapping.grid_forget()
        self.btn_save_img.grid_forget()                
        self.btn_rotateR.grid_forget()
        self.btn_rotateL.grid_forget()

    def key_press(self, event):
        if event.char == "s":
            self.save_image()
        elif event.char == 'p':
            self.to_panoramic()
        elif event.char == "w":
            self.to_unwrapping()
        elif event.char == "r":
            self.sample_extractor.reset_vertices()
            self.sample_extractor.refresh_image()
            photo_img = cv2.cvtColor(self.sample_extractor.get_image(), cv2.COLOR_BGR2RGB)
            photo_img = Image.fromarray(photo_img)
            img_for_label = ImageTk.PhotoImage(photo_img)
            self.label_extractor.configure(image=img_for_label)
            self.label_extractor.image = img_for_label
            self.label_extractor.grid(row=0, column=0, padx=10, pady=10)
    
    def release_click(self, event):
        self.sample_extractor.refresh_image()
        self.preview()

    def crop(self, image, mode):
        self.sample_extractor = SampleExtractor(self._resize_img(image), mode)
        #se ingresa en un canvas
        canvas_extractor = tkinter.Canvas(self.principal_fr)
        self.label_extractor = self.add_img_to_canvas(canvas_extractor, self.sample_extractor.get_image())
        self.label_extractor.bind('<1>', self.click_check)
        self.label_extractor.bind('<B1-Motion>',self.click_pos)
        self.label_extractor.bind('<ButtonRelease-1>', self.release_click)
        self.main_win.bind('<Key>',self.key_press)
        canvas_extractor.grid(row=0, column=0)

    def measures(self):
        self.entry_height_cm.grid(row=0, column=4)
        self.btn_height.grid(row=0, column=5)

    def un_measures(self):
        self.entry_height_cm.grid_forget()
        self.btn_height.grid_forget()

    def select_img(self):
        try:
            img = image_managers.load_image_from_window()
            #set max resolution
            #TODO: Move to another module
            resize_height = SCREEN_HEIGHT
            resize_width = SCREEN_WIDTH
            resize_img = img
            resize_scale = 4
            if img.shape[0] > resize_height:
                # Adjust image to the define height
                resize_img = cv2.resize(img, ((int(img.shape[1] * resize_height / img.shape[0])), int(resize_height)))
                # If its new width exceed the define width
            if resize_img.shape[1] > resize_width:
                # Adjust image to the define width
                resize_img = cv2.resize(resize_img, (int(resize_width), int(resize_img.shape[0] * resize_width / resize_img.shape[1])))

            self.org_img = resize_img
            self.clone_img = resize_img
            self.clean_principal_frame()
            self.clean_canvas_frame()
            self.clean_btns()
            
            self.crop(resize_img, ExtractorModeEnum.PANORAMIC)

            self.measures()
            self.btn_panoramic.grid(row=0, column=1)
            self.btn_unwrapping.grid(row=0, column=2)
            self.btn_save_img.grid(row=0, column=3)

            self.btn_rotateR.grid(row=2, column=5)
            self.btn_rotateL.grid(row=2, column=4)

            self.segmentation = False
            self.mode = 'p'
            self.grados = 0
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
        for wget in self.btns_fr.winfo_children():
            wget.grid_forget()
        self.btn_img.grid(row=0, column=0)
        

    def create_btns(self) -> None:
        # Set buttons positions
        self.btn_3d.grid(row=0, column=1, padx=5, pady=5)
        self.total_clusters.grid(row=0, column=2, padx=5, pady=5)
        self.btn_split.grid(row=0, column=3, padx=5, pady=5)
        self.btn_merge.grid(row=0, column=4, padx=5, pady=5)
        self.btn_sub.grid(row=0, column=5, padx=5, pady=5)
        self.btn_undo.grid(row=1,column=0, padx=5, pady=5)
        self.btn_save.grid(row=1, column=1, padx=5, pady=5)
        self.btn_up.grid(row=1, column=2, padx=5, pady=5)
        self.btn_down.grid(row=1, column=3, padx=5, pady=5)
        self.btn_update.grid(row=1, column=4, padx=5, pady=5)
        self.btn_analyze.grid(row=0, column=6, padx=5, pady=5)
        self.btn_segmentate.grid(row=1, column=6, padx=5, pady=5)

    def clean_principal_frame(self) -> None:
        """
        Destroy the principal frame and start a new one.
        """
        for wget in self.principal_fr.winfo_children():
            wget.destroy()
        self.principal_fr.destroy()
        self.principal_fr = ttk.Frame(self.main_win, style='Card.TFrame', padding=(5, 6, 7, 8))
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
        self.results_fr = ttk.Frame(self.canvas_fr, style='Card.TFrame', padding=(5, 6, 7, 8))
        self.img_container_fr.grid(row=1, column=2, sticky=tkinter.N+tkinter.E+tkinter.W+tkinter.S)
    
    def add_img_to_canvas(self, canvas: tkinter.Canvas, img: cv2.Mat) -> None:
        """
        Adds an image to the canvas.
        """
        photo_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        label_img = ttk.Label(canvas, image=img_for_label)
        label_img.image = img_for_label
        label_img.grid(row=0, column=0, padx=10, pady=10)
        return label_img
        
    def click(self, image: cv2.Mat, key: Any, canvas: tkinter.Canvas) -> None:
        """
        Handles the clicks on screen, unselecting previous images if needed
        or selecting new ones.
        """
        if key in self.selected_images_indices:
            self.selected_images_indices.remove(key)
            canvas.configure()
            for widget in canvas.winfo_children():
                if widget.cget("text"):
                    widget.destroy()
        else:
            self.selected_images_indices.append(key)
            canvas.configure()

            color_percent = percent.percent(image)
            widgetP = ttk.Label(canvas, text=f"Porcentaje de pixeles: {color_percent}%")
            widgetP.grid(row = 1,column=0 )

    def _resize_img(self, img):
        """
        Resize the image acording to the actual window size of the aplication.
        """
        # Get actual window size
        win_height = self.main_win.winfo_height()
        win_width = self.main_win.winfo_width()
        padding_size = 10
        resize_scale = 1
        # Define the desire height and width of the image
        resize_height = int((win_height - self.btn_fr_size - padding_size) * resize_scale // 2)
        resize_width = int((win_width - padding_size / 2) * resize_scale // 3)

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
            principal_canva = tkinter.Canvas(self.principal_fr, width=principal_image_res.shape[1], height=principal_image_res.shape[0])
            self.add_img_to_canvas(principal_canva, principal_image_res)
            principal_canva.grid(row=0, column=0)

            self.segmentated = self._resize_img(self.segmentated)
            canva = tkinter.Canvas(self.principal_fr, width=self.segmentated.shape[1], height=self.segmentated.shape[0])
            self.add_img_to_canvas(canva, self.segmentated)
            if self.segmentated.shape[0] > self.segmentated.shape[1]:
                canva.grid(row=0, column=1)
            else:
                canva.grid(row=1, column=0)
            
        else:
            self.clean_canvas_frame()
            # Set image for cropped image frame
            canva = tkinter.Canvas(self.principal_fr, width=img.shape[1], height=img.shape[0])
            _ = self.add_img_to_canvas(canva, img)
            canva.grid(row=0, column=0)

            # draws image node childs
            img_row_shape = 2
            i = 0
            for child in self.img_tree.childs:
                child_img = self._resize_img(child.image)
                child_img = cv2.resize(child.image, (int(child_img.shape[1]*CLUSTER_RESHAPE), int(child_img.shape[0]*CLUSTER_RESHAPE)))
                canva = tkinter.Canvas(self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0])
                label = self.add_img_to_canvas(canva, child_img)
                label.bind('<ButtonPress-1>', lambda event, image=child.image, key=i, canvas=canva: self.click(image, key, canvas))
                canva.grid(row=i%img_row_shape, column=i//img_row_shape)
                i+=1

    def merge(self) -> None:
        """
        This method merges 2 or more clusters, updating the image tree.
        """
        if len(self.selected_images_indices) < 2:
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione 2 o más imágenes.")
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
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione al menos una imagen.")
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
        # tkinter.messagebox.showinfo("Proximamente", message="Esta funcionalidad estará disponible proximamente.")

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
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione una imagen.")
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
            tkinter.messagebox.showwarning("Error", message="Esta es la imagen original.")
            return
        self.img_tree = self.img_tree.parent
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()
    
    def analyze(self) -> None:
        """
        This method is in charge of the shape detection at a cluster.
        """
        if len(self.selected_images_indices) > 1:
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione solo una imagen.")
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]

        self.clean_principal_frame()
        self.clean_canvas_frame()

        self.selected_images_indices = []
        self.segmentation = True

        self.contour = sc.contour_segmentation(self.img_tree.image)
        self.segmentated = sc.cluster_segmentation(self.img_tree.image,self.contour, sc.DEF_COLOR)

        self.update_screen()

        results = sc.generate_results(self.contour, self.height_cm/self.segmentated.shape[0])
        self.fill_table(results, sc.DEF_COLOR)

    def segmentate(self) -> None:
        """
        This method is in charge of the shape segmentation at a cluster.
        """
        if len(self.selected_images_indices) > 1:
            tkinter.messagebox.showwarning("Error", message="Por favor, seleccione solo una imagen.")
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        
        self.clean_principal_frame()
        self.clean_canvas_frame()

        self.selected_images_indices = []
        self.segmentation = True
        
        self.contour = sc.contour_segmentation(self.img_tree.image)
        sc.contour_agrupation(self.contour)
        self.segmentated = sc.cluster_segmentation(self.img_tree.image,self.contour, sc.COLORS)

        self.update_screen()

        results = sc.generate_results(self.contour, self.height_cm/self.segmentated.shape[0])
        self.fill_table(results, sc.COLORS)

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
            if color_count[i] == 0:
                agg_results[i] = None
                continue
            for j in range(len(sc.STATISTICS)):
                agg_results[i][j] /= color_count[i]
                agg_results[i][j] = np.round(agg_results[i][j], 2)
        return agg_results

    def create_label(self, name, row, col):
        label = ttk.Label(self.results_fr, text=name, style="Heading.TLabel", padding=(5, 6, 7, 8))
        label.grid(row=row, column=col)
        return label
    
    def create_color_label(self, name, row, col):
        label = tkinter.Label(self.results_fr, text=name, highlightthickness=1, highlightbackground="black")
        label.grid(row=row, column=col, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
        return label

    def fill_table(self, results, colors) -> None:
        """
        This method fills and shows a table at the GUI.
        The data is given as an input.
        """
        aggregated_results = self.aggregate(results)
        self.results_fr.grid(row=0,column=0)
        self.img_container_canvas.xview('moveto', 0)
        self.create_label("Color", 0, 0)
        self.create_label("Mineral", 0, 1)
        for i in range(len(sc.STATISTICS)):
            self.create_label(sc.STATISTICS[i], 0, i+2)
        
        for row_num in range(len(aggregated_results)):
            if aggregated_results[row_num] == None:
                continue
            (b, g, r) = colors[row_num]
            color = '#%02x%02x%02x' % (r, g, b)

            label_color = self.create_color_label("", row_num+1, 0)
            label_color.config(bg=color, width=1, height=1, justify=tkinter.CENTER)
            name = PlaceholderEntry(self.results_fr, f"Mineral {row_num}")
            name.grid(row=row_num+1, column=1, sticky=tkinter.W+tkinter.E)

            for col_num in range(len(sc.STATISTICS)):
                self.create_label(aggregated_results[row_num][col_num], row_num+1, col_num+2)

        self.btnExport = ttk.Button(self.results_fr, text="Descargar", width=15, command=lambda : self.table_to_csv(results) , cursor='arrow')
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
        tkinter.messagebox.showinfo("Guardado", message="Los resultados se han guardado correctamente")
    
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
        tkinter.messagebox.showinfo("Guardado", message="Las imagenes se han guardado correctamente")
    def rotate_image(self) -> None:
        self.clean_principal_frame()
        self.org_img =  cv2.rotate(self.org_img, cv2.ROTATE_90_CLOCKWISE)
        self.crop(self.org_img)



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

sv_ttk.set_theme("dark")
ROOT.mainloop()