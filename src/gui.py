import csv
import tkinter
import tkinter.font as tk_font
import tkinter.messagebox
import webbrowser
from tkinter import ttk
from typing import Any, List

import cv2
import numpy as np
import sv_ttk
from PIL import Image, ImageTk

import image_managers
import image_tree
import percent
import shape_detection as sc
import tube
from sample_extraction import ExtractorModeEnum, SampleExtractor
from utils import (PlaceholderEntry, createBalloon, createButtonWithHover,
                   createCheckBoxWithHover, generate_zip, get_file_filepath,
                   get_path, get_results_filepath)

CLUSTER_RESHAPE = 0.7
ROOT = tkinter.Tk()
SCREEN_WIDTH = ROOT.winfo_screenwidth()
SCREEN_HEIGHT = ROOT.winfo_screenheight()
ARROW_LEFT = tkinter.PhotoImage(file=get_path("./assets/left_arrow.png"))
ARROW_RIGHT = tkinter.PhotoImage(file=get_path("./assets/right_arrow.png"))
HELP_ICON = tkinter.PhotoImage(file=get_path("./assets/help_icon.png"))
OFF = tkinter.PhotoImage(file=get_path("./assets/off.png"))
ON = tkinter.PhotoImage(file=get_path("./assets/on.png"))


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

        self.sample_extractor = SampleExtractor()

        self.img_tree = None
        self.selected_images_indices = []
        self.main_win = root
        self.main_win.bind("<1>", self.focus_win)
        self.key_pressed = ""
        self.clicked_pos = (0, 0)
        # --- interface parameters ---

        # -- fonts --
        self.my_font = tk_font.Font(size=14)
        self.title_font = tk_font.Font(size=20)
        self.data_font = tk_font.Font(size=16)
        self.section_font = tk_font.Font(size=10)

        # -- frames --
        self.btns_fr = ttk.Frame(
            self.main_win, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.btns_fr.grid(
            row=0, column=1, columnspan=3, padx=10, pady=10, sticky=tkinter.NW
        )

        self.file_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.file_fr.grid(row=0, column=0, sticky=tkinter.N)
        self.command_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.crop_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.size_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.size_sub_fr = ttk.Frame(
            self.size_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.color_seg_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.image_tools_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.gen_results_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.navigate_fr = ttk.Frame(
            self.main_win, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.help_fr = ttk.Frame(
            self.btns_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )

        for i in range(6):
            self.btns_fr.columnconfigure(i, weight=1)
        self.file_fr.columnconfigure(0, weight=1)
        self.command_fr.columnconfigure(0, weight=1)
        self.command_fr.columnconfigure(1, weight=1)
        self.crop_fr.columnconfigure(0, weight=1)
        self.size_fr.columnconfigure(0, weight=1)
        self.size_sub_fr.columnconfigure(0, weight=1)
        self.size_sub_fr.columnconfigure(1, weight=1)
        self.color_seg_fr.columnconfigure(0, weight=1)
        self.color_seg_fr.columnconfigure(1, weight=1)
        self.image_tools_fr.columnconfigure(0, weight=1)
        self.gen_results_fr.columnconfigure(0, weight=1)
        self.navigate_fr.columnconfigure(0, weight=1)
        self.help_fr.columnconfigure(0, weight=1)
        self.btns_fr.columnconfigure(5, minsize=50)

        self.img_container_fr = ttk.Frame(
            self.main_win, style="Card.TFrame", padding=(5, 6, 7, 8)
        )

        self.img_container_canvas = tkinter.Canvas(self.img_container_fr)

        self.canvas_fr = ttk.Frame(
            self.img_container_canvas, style="Card.TFrame", padding=(5, 6, 7, 8)
        )

        self.principal_fr = ttk.Frame(
            self.main_win, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.principal_fr.grid(row=1, column=1, sticky=tkinter.N)

        self.results_fr = ttk.Frame(
            self.canvas_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )

        # -- buttons --
        btn_img_name = "Seleccionar imagen"
        btn_img_description = "Permite abrir una imagen desde su PC."
        self.btn_img, self.hover_img = createButtonWithHover(
            self.file_fr, btn_img_name, self.select_img, btn_img_description
        )
        self.btn_img.grid(row=0, column=0, padx=5, pady=5)
        self.btn_img.config(style="Accent.TButton")

        btn_save_img_name = "Recortar"
        btn_save_img_description = (
            "Recorta la imagen encerrada en el rectangulo que se ve en pantalla."
        )
        self.btn_save_img, self.hover_save_img = createButtonWithHover(
            self.command_fr,
            btn_save_img_name,
            self.save_image,
            btn_save_img_description,
        )

        btn_reset_img_name = "Restablecer"
        btn_reset_img_description = (
            "Reestablece la posición de los puntos usados para recortar la imagen."
        )
        self.btn_reset_img, self.hover_reset_img = createButtonWithHover(
            self.command_fr,
            btn_reset_img_name,
            self.reset_image,
            btn_reset_img_description,
        )

        btn_rotate_name = "Girar"
        btn_rotate_description = (
            "Gira 90 grados la imagen a recortar en sentido horario."
        )
        self.btn_rotate, self.hover_rotate = createButtonWithHover(
            self.command_fr, btn_rotate_name, self.rotate_image, btn_rotate_description
        )

        btn_select_all_img_name = "Seleccionar todo"
        btn_select_all_img_description = "Mueve los puntos a las esquinas de la imagen"
        self.btn_select_all_img, self.hover_select_all_img = createButtonWithHover(
            self.command_fr,
            btn_select_all_img_name,
            self.select_all_img,
            btn_select_all_img_description,
        )

        btn_rotateR_name = "Rotar imagen R"
        btn_rotateR_description = "gira levemente la imagen en sentido horario"
        self.btn_rotateR, self.hover_rotateR = createButtonWithHover(
            self.command_fr, btn_rotateR_name, self.rotateR, btn_rotateR_description
        )

        btn_rotateL_name = "Rotar imagen L"
        btn_rotateL_description = "gira levemente la imagen en sentido antihorario"
        self.btn_rotateL, self.hover_rotateL = createButtonWithHover(
            self.command_fr, btn_rotateL_name, self.rotateL, btn_rotateL_description
        )

        btn_panoramic_name = "Modo panorámico"
        btn_panoramic_description = "Es necesario posicionar 4 puntos para realizar un recorte sin ajuste de perspectiva."
        self.btn_panoramic, self.hover_panoramic = createButtonWithHover(
            self.crop_fr,
            btn_panoramic_name,
            self.to_panoramic,
            btn_panoramic_description,
        )

        btn_unwrapping_name = "Modo unwrapping"
        btn_unwrapping_description = "Es necesario posicionar 6 puntos para realizar un recorte con ajuste de perspectiva."
        self.btn_unwrapping, self.hover_unwrapping = createButtonWithHover(
            self.crop_fr,
            btn_unwrapping_name,
            self.to_unwrapping,
            btn_unwrapping_description,
        )

        btn_rectangle_name = "Modo rectangular"
        btn_rectangle_description = "Si"
        self.btn_rectangle, self.hover_rectangle = createButtonWithHover(
            self.crop_fr,
            btn_rectangle_name,
            self.to_rectangle,
            btn_rectangle_description,
        )

        btn_height_name = "Altura(cm)"
        btn_height_description = (
            "Permite guardar la altura (en cm) de la roca introducida."
        )
        self.btn_height, self.hover_height = createButtonWithHover(
            self.size_sub_fr, btn_height_name, self.set_height, btn_height_description
        )

        btn_save_name = "Guardar"
        btn_save_description = "Guarda la imagen actual junto con las imágenes obtenidas al segmentar por color."
        self.btn_save, self.hover_save = createButtonWithHover(
            self.file_fr, btn_save_name, self.save, btn_save_description
        )

        btn_split_name = "Separar"
        btn_split_description = "Segmenta la imagen por colores, generando una cantidad de imagenes igual al número ingresado."
        self.btn_split, self.hover_split = createButtonWithHover(
            self.color_seg_fr, btn_split_name, self.split, btn_split_description
        )

        btn_merge_name = "Combinar"
        btn_merge_description = "Permite combinar 2 o más imagenes en una sola."
        self.btn_merge, self.hover_merge = createButtonWithHover(
            self.color_seg_fr, btn_merge_name, self.merge, btn_merge_description
        )

        btn_sub_name = "Eliminar"
        btn_sub_description = "Permite eliminar 1 o más imagenes, también se refleja en la imagen original."
        self.btn_sub, self.hover_sub = createButtonWithHover(
            self.color_seg_fr, btn_sub_name, self.delete, btn_sub_description
        )

        btn_update_name = "Actualizar"
        btn_update_description = "Actualiza la pantalla, ajustando el tamaño de las imágenes presentes en ella."
        self.btn_update, self.hover_update = createButtonWithHover(
            self.image_tools_fr,
            btn_update_name,
            self.update_screen,
            btn_update_description,
        )

        btn_undo_name = "Deshacer"
        btn_undo_description = "Deshace todos los cambios hechos sobre la imagen."
        self.btn_undo, self.hover_undo = createButtonWithHover(
            self.image_tools_fr, btn_undo_name, self.undo, btn_undo_description
        )

        btn_3d_name = "3D"
        btn_3d_description = (
            "Permite visualizar en 3D la imagen que se encuentra en la pantalla."
        )
        self.btn_3d, self.hover_3d = createButtonWithHover(
            self.gen_results_fr, btn_3d_name, self.plot_3d, btn_3d_description
        )

        btn_analyze_name = "Analizar"
        btn_analyze_description = "Permite analizar la imagen seleccionada, calculando las estadisticas presentes en el programa."
        self.btn_analyze, self.hover_analyze = createButtonWithHover(
            self.gen_results_fr,
            btn_analyze_name,
            self.process_image,
            btn_analyze_description,
        )

        toggle_seg_name = "Segmentar por formas"
        toggle_seg_description = "Permite activar o desactivar la segmentacion por formas al momento de analizar la imagen seleccionada."
        self.toggle_var = tkinter.BooleanVar()
        self.toggle_seg, self.hover_toggle = createCheckBoxWithHover(
            self.gen_results_fr,
            toggle_seg_name,
            toggle_seg_description,
            self.toggle_var,
        )

        btn_back_name = "Atras"
        btn_back_description = "Permite acceder a la imagen que se tenia anteriormente."
        self.btn_back, self.hover_back = createButtonWithHover(
            self.navigate_fr,
            btn_back_name,
            self.back,
            btn_back_description,
            image=ARROW_LEFT,
        )

        btn_forward_name = "Adelante"
        btn_forward_description = (
            "Permite cambiar la imagen actual por la imagen seleccionada."
        )
        self.btn_forward, self.hover_forward = createButtonWithHover(
            self.navigate_fr,
            btn_forward_name,
            self.forward,
            btn_forward_description,
            image=ARROW_RIGHT,
        )

        btn_doc_name = "Ayuda"
        btn_doc_description = (
            "Permite abrir la documentación completa de la aplicación."
        )
        self.btn_doc, self.hover_doc = createButtonWithHover(
            self.help_fr,
            btn_doc_name,
            self.view_documentation,
            btn_doc_description,
            image=HELP_ICON,
        )

        # -- entries --
        self.total_clusters = PlaceholderEntry(self.color_seg_fr, "3")
        self.total_clusters["font"] = self.my_font

        self.entry_height_cm = PlaceholderEntry(self.size_sub_fr, "20")
        self.entry_height_cm["font"] = self.my_font

        # -- labels --
        self.file_fr_lbl = tkinter.Label(
            self.file_fr, text="Archivos", font=self.section_font
        )
        self.file_fr_lbl.grid(column=0)
        self.command_fr_lbl = tkinter.Label(
            self.command_fr, text="Comandos", font=self.section_font
        )
        self.crop_fr_lbl = tkinter.Label(
            self.crop_fr, text="Modo de\n recorte", font=self.section_font
        )
        self.size_fr_lbl = tkinter.Label(
            self.size_fr, text="Tamaño", font=self.section_font
        )
        self.color_seg_lb = tkinter.Label(
            self.color_seg_fr, text="Segmentación color", font=self.section_font
        )
        self.image_tools_lb = tkinter.Label(
            self.image_tools_fr, text="Modificar imagen", font=self.section_font
        )
        self.gen_results_lb = tkinter.Label(
            self.gen_results_fr, text="Generación \n resultados", font=self.section_font
        )
        self.navigate_lb = tkinter.Label(
            self.navigate_fr, text="Navegar", font=self.section_font
        )

        # -- extras --
        self.set_up_scrollbar()
        self.btn_fr_size = 200
        self.segmentation = False
        self.height_mm = 200
        self.grados = 0
        self.canvas_preview = tkinter.Canvas(self.principal_fr)
        self.prev_boolean = False
        self.cm = False
        self.switch_btn_image = OFF

    def set_height(self):
        try:
            self.height_mm = float(self.entry_height_cm.get()) * 10
        except Exception as e:
            print(e)
            tkinter.messagebox.showwarning(
                "Error", message="Por favor ingresa un número."
            )
            return

    def focus_win(self, event):
        if not isinstance(event.widget, ttk.Entry):
            self.main_win.focus()

    def set_up_scrollbar(self):
        """
        Sets up the scrollbar of the gui, instantiating ttk.Scrollbar
        and positioning it.
        """
        self.scrollbar = ttk.Scrollbar(
            self.img_container_fr,
            orient=tkinter.HORIZONTAL,
            command=self.img_container_canvas.xview,
        )

        self.canvas_fr.bind(
            "<Configure>",
            lambda _: self.img_container_canvas.configure(
                scrollregion=self.img_container_canvas.bbox("all")
            ),
        )

        self.img_container_canvas.create_window(
            (0, 0), window=self.canvas_fr, anchor="nw"
        )

        self.main_win.columnconfigure(3, weight=1)
        self.main_win.rowconfigure(1, weight=1)

        self.img_container_fr.columnconfigure(0, weight=1)
        self.img_container_fr.rowconfigure(0, weight=1)
        self.img_container_canvas.configure(xscrollcommand=self.scrollbar.set)

        self.img_container_canvas.grid()

        self.canvas_fr.bind("<Enter>", self._bound_to_mousewheel)
        self.canvas_fr.bind("<Leave>", self._unbound_to_mousewheel)

        self.img_container_canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=0, sticky=tkinter.N + tkinter.EW)
        self.img_container_canvas.grid(
            row=0, column=0, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )

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
        self.img_container_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def split(self) -> None:
        """
        Splits the current image by doing KMeans clustering on it. The number of clusters
        is given by the user by filling the 'total_clusters' entry.
        """
        try:
            n_childs = int(self.total_clusters.get())
        except:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor ingresa un número."
            )
            return
        selected_imgs = len(self.selected_images_indices)

        if selected_imgs > 1:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione solo una imagen."
            )
            return

        if selected_imgs == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]

        self.img_tree.split(n_childs=n_childs)
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def click_check(self, event):
        self.sample_extractor.check_mov(event.x, event.y)

    def click_pos(self, event):
        self.sample_extractor.move_vertex(event.x, event.y)
        self.update_image(self.label_extractor, self.sample_extractor.get_image())

    def choose_cut_method(self, img):
        return self.sample_extractor.cut(img)

    def select_all_img(self):
        self.sample_extractor.to_corners()

        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())
        self.preview()

    def rotateR(self):
        image_center = tuple(np.array(self.clone_img.shape[1::-1]) / 2)
        self.grados -= 0.2
        rotation_matrix = cv2.getRotationMatrix2D(
            image_center, angle=self.grados, scale=1
        )
        self.rot_img = cv2.warpAffine(
            self.clone_img,
            rotation_matrix,
            (self.clone_img.shape[1], self.clone_img.shape[0]),
        )

        self.sample_extractor.set_image(self._resize_img(self.rot_img), rotation=True)
        self.sample_extractor.reset_vertices()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())
        self.preview()

    def rotateL(self):
        image_center = tuple(np.array(self.clone_img.shape[1::-1]) / 2)
        self.grados += 0.2
        rotation_matrix = cv2.getRotationMatrix2D(
            image_center, angle=self.grados, scale=1
        )
        self.rot_img = cv2.warpAffine(
            self.clone_img,
            rotation_matrix,
            (self.clone_img.shape[1], self.clone_img.shape[0]),
        )

        self.sample_extractor.set_image(self._resize_img(self.rot_img), rotation=True)
        self.sample_extractor.reset_vertices()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())
        self.preview()

    def update_image(self, label, image):
        photo_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        label.configure(image=img_for_label)
        label.image = img_for_label
        label.grid(row=0, column=0, padx=10, pady=10)

    def preview(self):
        if hasattr(self, "canvas_preview"):
            self.canvas_preview.destroy()
            self.canvas_preview = tkinter.Canvas(self.principal_fr)
            copy_img = self.choose_cut_method(self.org_img)
            copy_img = self._resize_img(copy_img, 1.7)
            self.label_extractor2 = self.add_img_to_canvas(
                self.canvas_preview, copy_img
            )
            self.canvas_preview.grid(row=0, column=1)
            self.update_image(self.label_extractor2, copy_img)
            return
        self.canvas_preview = tkinter.Canvas(self.principal_fr)
        copy_img = self.choose_cut_method(self.org_img)
        self.label_extractor2 = self.add_img_to_canvas(
            self.canvas_preview, self._resize_img(copy_img, 1.7)
        )
        self.canvas_preview.grid(row=0, column=1)

    def save_image(self):
        if self.height_mm is None:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor ingresa la altura."
            )
            return
        self.prev_boolean = False
        self.org_img = self.choose_cut_method(self.org_img)
        self.main_win.unbind("<Key>")
        self.un_measures()
        for wget in self.file_fr.winfo_children():
            wget.grid_forget()
        self.file_fr.grid_forget()
        for wget in self.command_fr.winfo_children():
            wget.grid_forget()
        self.command_fr.grid_forget()
        for wget in self.crop_fr.winfo_children():
            wget.grid_forget()
        self.crop_fr.grid_forget()
        for wget in self.size_fr.winfo_children():
            wget.grid_forget()
        self.size_fr.grid_forget()
        self.show_img()

    def reset_image(self):
        self.clone_img = self.org_img
        self.rot_img = self.org_img
        self.grados = 0
        self.sample_extractor.set_image(self._resize_img(self.org_img), rotation=True)
        self.sample_extractor.reset_vertices()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())
        self.preview()

    def key_press(self, event):
        if event.char == "s":
            self.save_image()
        elif event.char == "p":
            self.to_panoramic()
        elif event.char == "w":
            self.to_unwrapping()
        elif event.char == "r":
            self.reset_image()

    def release_click(self, event):
        copy_img = self.choose_cut_method(self.org_img)
        self.update_image(self.label_extractor2, self._resize_img(copy_img, 1.7))
        self.sample_extractor.refresh_image()

    def _set_extractor_canvas(self):
        canvas_extractor = tkinter.Canvas(self.principal_fr)
        self.label_extractor = self.add_img_to_canvas(
            canvas_extractor, self.sample_extractor.get_image()
        )
        self.label_extractor.bind("<1>", self.click_check)
        self.label_extractor.bind("<B1-Motion>", self.click_pos)
        self.label_extractor.bind("<ButtonRelease-1>", self.release_click)
        self.main_win.bind("<Key>", self.key_press)
        canvas_extractor.grid(row=0, column=0, sticky=tkinter.N)
        self.preview()

    def crop(self):
        self.sample_extractor.init_extractor()

        # insert in  canvas
        self._set_extractor_canvas()

    def measures(self):
        self.size_fr.grid(row=0, column=4, sticky=tkinter.N)
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
            img, filename = image_managers.load_image_from_window()
            self.filename = filename.split("/")[-1].split(".")[0]
            # set max resolution
            # TODO: Move to another module
            resize_height = SCREEN_HEIGHT
            resize_width = SCREEN_WIDTH
            resize_img = img
            resize_scale = 4
            if img.shape[0] > resize_height:
                # Adjust image to the define height
                resize_img = cv2.resize(
                    img,
                    (
                        (int(img.shape[1] * resize_height / img.shape[0])),
                        int(resize_height),
                    ),
                )
                # If its new width exceed the define width
            if resize_img.shape[1] > resize_width:
                # Adjust image to the define width
                resize_img = cv2.resize(
                    resize_img,
                    (
                        int(resize_width),
                        int(resize_img.shape[0] * resize_width / resize_img.shape[1]),
                    ),
                )

            self.org_img = resize_img
            self.clone_img = resize_img
            self.rot_img = resize_img

            self.clean_principal_frame()
            self.clean_canvas_frame()
            self.clean_btns()

            self.sample_extractor.set_image(self._resize_img(resize_img))
            self.crop()

            self.measures()

            # -- File managment
            self.file_fr.grid(row=0, column=0, sticky=tkinter.N)
            self.btn_img.grid(row=0, column=0, padx=5, pady=5)
            self.file_fr_lbl.grid(column=0)
            # -- commands --
            self.command_fr.grid(row=0, column=1, sticky=tkinter.N)
            self.btn_save_img.grid(row=0, column=0, padx=5, pady=5)
            self.btn_reset_img.grid(row=1, column=0, padx=5, pady=5)
            self.btn_select_all_img.grid(row=1, column=1, padx=5, pady=5)
            self.btn_rotate.grid(row=0, column=1, padx=5, pady=5)
            self.btn_rotateR.grid(row=0, column=2, padx=5, pady=5)
            self.btn_rotateL.grid(row=1, column=2, padx=5, pady=5)
            self.command_fr_lbl.grid(column=0, padx=5, pady=5, columnspan=3)
            # -- crop types --
            self.crop_fr.grid(row=0, column=2, sticky=tkinter.N)
            self.btn_panoramic.grid(row=0, column=0, padx=5, pady=5)
            self.btn_unwrapping.grid(row=1, column=0, padx=5, pady=5)
            self.btn_rectangle.grid(row=2, column=0, padx=5, pady=5)
            self.crop_fr_lbl.grid(column=0, padx=5, pady=5)
            # -- help --
            self.help_fr.grid(row=0, column=5, sticky=tkinter.N)
            self.btn_doc.grid(row=0, column=0, padx=5, pady=5)

            self.segmentation = False
            self.grados = 0
            self.height_mm = 200
        except:
            pass

    def show_img(self) -> None:
        """
        This method is called when a new image is uploaded.
        """
        # self.clean_frames()
        self.img_tree = image_tree.ImageNode(None, self.org_img, self.filename)
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
        self.file_fr.grid(row=0, column=0, sticky=tkinter.N)
        self.btn_img.grid(row=0, column=0, padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, padx=5, pady=5)
        self.file_fr_lbl.grid(column=0, padx=5, pady=5)

        # -- Color Segmentation --
        self.color_seg_fr.grid(row=0, column=1, sticky=tkinter.N)
        self.total_clusters.grid(row=0, column=0, padx=5, pady=5, ipadx=2, ipady=5)
        self.btn_split.grid(row=0, column=1, padx=5, pady=5)
        self.btn_merge.grid(row=1, column=0, padx=5, pady=5)
        self.btn_sub.grid(row=1, column=1, padx=5, pady=5)
        self.color_seg_lb.grid(padx=5, pady=5, columnspan=2)

        # -- Image Tools
        self.image_tools_fr.grid(row=0, column=3, sticky=tkinter.N)
        self.btn_update.grid(row=0, column=0, padx=5, pady=5)
        self.btn_undo.grid(row=1, column=0, padx=5, pady=5)
        self.image_tools_lb.grid(column=0, padx=5, pady=5)

        # -- Results generation --
        self.gen_results_fr.grid(row=0, column=4, sticky=tkinter.N)
        self.btn_3d.grid(row=0, column=0, padx=5, pady=5)
        self.btn_analyze.grid(row=1, column=0, padx=5, pady=5)
        self.toggle_seg.grid(row=2, column=0, padx=5, pady=5)
        self.gen_results_lb.grid(column=0, padx=5, pady=5)

        # -- Navigate --
        self.navigate_fr.grid(row=1, column=1, sticky=tkinter.N)
        self.btn_back.grid(row=0, column=0, padx=5, pady=5)
        self.btn_forward.grid(row=0, column=1, padx=5, pady=5)
        self.navigate_lb.grid(column=0, padx=5, pady=5, columnspan=2)

        # -- Help --
        self.help_fr.grid(row=0, column=5, sticky=tkinter.N)
        self.btn_doc.grid(row=0, column=0, padx=5, pady=5)

    def clean_principal_frame(self) -> None:
        """
        Destroy the principal frame and start a new one.
        """
        for wget in self.principal_fr.winfo_children():
            wget.destroy()
        self.principal_fr.destroy()
        self.principal_fr = ttk.Frame(
            self.main_win, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.principal_fr.grid(row=1, column=2, sticky=tkinter.N)

    def clean_canvas_frame(self) -> None:
        """
        Destroy every tkinter instance inside the canvas frame
        and start new one.
        """
        for wget in self.results_fr.winfo_children():
            wget.destroy()

        for wget in self.canvas_fr.winfo_children():
            wget.destroy()
        self.results_fr = ttk.Frame(
            self.canvas_fr, style="Card.TFrame", padding=(5, 6, 7, 8)
        )
        self.img_container_fr.grid(
            row=1, column=3, sticky=tkinter.N + tkinter.E + tkinter.W + tkinter.S
        )

    def add_img_to_canvas(self, canvas: tkinter.Canvas, img: cv2.Mat) -> None:
        """
        Adds an image to the canvas.
        """
        photo_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        photo_img = Image.fromarray(photo_img)
        img_for_label = ImageTk.PhotoImage(photo_img)
        label_img = ttk.Label(canvas, image=img_for_label)
        label_img.image = img_for_label
        label_img.grid(row=0, column=0, padx=10, pady=5)
        return label_img

    def click(self, image: cv2.Mat, key: Any, canvas: tkinter.Canvas) -> None:
        """
        Handles the clicks on screen, unselecting previous images if needed
        or selecting new ones.
        """
        if key in self.selected_images_indices:
            self.selected_images_indices.remove(key)
            canvas.configure(bg="white")
            for widget in canvas.winfo_children():
                if widget.cget("text"):
                    widget.destroy()
        else:
            self.selected_images_indices.append(key)
            canvas.configure(bg="red")

            color_percent = percent.percent(image)
            widgetP = ttk.Label(canvas, text=f"Porcentaje de pixeles: {color_percent}%")
            widgetP.grid(row=1, column=0)

    def _resize_img(self, img, resize_scale: float = 1):
        """
        Resize the image acording to the actual window size of the aplication.
        """
        # Get actual window size
        win_height = self.main_win.winfo_height()
        win_width = self.main_win.winfo_width()
        padding_size = 10

        # Define the desire height and width of the image
        resize_height = int(
            (win_height - self.btn_fr_size - padding_size) * resize_scale // 2
        )
        resize_width = int((win_width - padding_size / 2) * resize_scale // 3)

        # If the larger size of the image is its height (type TUBE)
        if img.shape[0] > img.shape[1]:
            # Adjust image to the define height
            resize_img = cv2.resize(
                img, ((int(img.shape[1] * resize_height / img.shape[0])), resize_height)
            )
            # If its new width exceed the define width
            if resize_img.shape[1] > resize_width:
                # Adjust image to the define width
                resize_img = cv2.resize(
                    resize_img,
                    (
                        resize_width,
                        int(resize_img.shape[0] * resize_width / resize_img.shape[1]),
                    ),
                )
        # If the larger size of the image is its width (type PANORAMIC)
        else:
            # Adjust image to the define width
            resize_img = cv2.resize(
                img, (resize_width, int(img.shape[0] * resize_width / img.shape[1]))
            )
            # If its new height exceed the define height
            if resize_img.shape[0] > resize_height:
                # Adjust image to the define height
                resize_img = cv2.resize(
                    resize_img,
                    (
                        (
                            int(
                                resize_img.shape[1]
                                * resize_height
                                / resize_img.shape[0]
                            )
                        ),
                        resize_height,
                    ),
                )

        return resize_img

    def update_screen(self) -> None:
        """
        Updates the screen, this method is called right after
        the user interacts with the current image.
        """
        self.clean_principal_frame()

        img = self._resize_img(
            self.img_tree.image
        )  # image at the current node of the image_tree

        if self.segmentation:
            principal_image = self.img_tree.image
            principal_image_res = self._resize_img(principal_image)
            principal_canva = tkinter.Canvas(
                self.principal_fr,
                width=principal_image_res.shape[1],
                height=principal_image_res.shape[0],
            )
            principal_label = tkinter.Label(self.principal_fr, text=self.img_tree.name)
            self.add_img_to_canvas(principal_canva, principal_image_res)
            principal_canva.grid(row=0, column=0)

            segmentated_img = self._resize_img(self.segmentated)
            canva = tkinter.Canvas(
                self.principal_fr,
                width=segmentated_img.shape[1],
                height=segmentated_img.shape[0],
            )
            canva_label = tkinter.Label(
                self.principal_fr, text=f"{self.img_tree.name} segmentada"
            )
            self.add_img_to_canvas(canva, segmentated_img)
            if segmentated_img.shape[0] > segmentated_img.shape[1]:
                canva.grid(row=0, column=1)
                principal_label.grid(row=1, column=0)
                canva_label.grid(row=1, column=1)
            else:
                canva.grid(row=2, column=0)
                principal_label.grid(row=1, column=0)
                canva_label.grid(row=3, column=0)

        else:
            self.clean_canvas_frame()
            # Set image for cropped image frame
            canva = tkinter.Canvas(
                self.principal_fr, width=img.shape[1], height=img.shape[0]
            )
            _ = self.add_img_to_canvas(canva, img)
            canva.grid(row=0, column=0)
            principal_label = tkinter.Label(self.principal_fr, text=self.img_tree.name)
            principal_label.grid(row=1, column=0)

            # draws image node childs
            img_row_shape = 2
            i = 0
            for child in self.img_tree.childs:
                child_img = self._resize_img(child.image)
                child_img = cv2.resize(
                    child.image,
                    (
                        int(child_img.shape[1] * CLUSTER_RESHAPE),
                        int(child_img.shape[0] * CLUSTER_RESHAPE),
                    ),
                )
                canva = tkinter.Canvas(
                    self.canvas_fr, width=child_img.shape[1], height=child_img.shape[0]
                )
                label = self.add_img_to_canvas(canva, child_img)
                label.bind(
                    "<ButtonPress-1>",
                    lambda event, image=child.image, key=i, canvas=canva: self.click(
                        image, key, canvas
                    ),
                )
                canva.grid(row=2 * (i % img_row_shape), column=i // img_row_shape)
                name_label = tkinter.Label(self.canvas_fr, text=child.name)
                name_label.grid(
                    row=2 * (i % img_row_shape) + 1, column=i // img_row_shape
                )
                if i in self.selected_images_indices:
                    label.event_generate("<ButtonPress-1>")
                    label.event_generate("<ButtonPress-1>")
                i += 1

    def merge(self) -> None:
        """
        This method merges 2 or more clusters, updating the image tree.
        """
        if len(self.selected_images_indices) < 2:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione 2 o más imagenes."
            )
            return
        self.img_tree.merge(self.selected_images_indices)
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def delete(self) -> None:
        """
        This method deletes at least 1 cluster, updating the image tree.
        """
        if len(self.selected_images_indices) == 0:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione al menos una imagen."
            )
            return
        self.img_tree.delete(self.selected_images_indices)
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

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
        self.img_tree = image_tree.ImageNode(None, self.org_img, self.filename)
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def forward(self) -> None:
        """
        Travels one level downwards in the image tree, this means that the GUI
        will show a cluster as a main image and the user will be able to
        call functions on it.
        """
        if len(self.selected_images_indices) != 1:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione una imagen."
            )
            return
        self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]
        self.last_index_selected.append(self.selected_images_indices[0])
        self.selected_images_indices = []
        self.segmentation = False
        self.update_screen()

    def back(self) -> None:
        """
        Travels one level upwards in the image tree, updates the GUI showing all the data
        related to the parent of the current node.
        """
        if self.img_tree.parent == None:
            tkinter.messagebox.showwarning(
                "Error", message="Esta es la imagen original."
            )
            return
        self.img_tree = self.img_tree.parent
        self.segmentation = False
        self.selected_images_indices = [self.last_index_selected.pop()]
        self.update_screen()

    def process_image(self):
        if self.toggle_var.get() == 1:
            self.segmentate()
        else:
            self.analyze()

    def analyze(self) -> None:
        """
        This method is in charge of the shape detection at a cluster.
        """
        if len(self.selected_images_indices) > 1:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione solo una imagen."
            )
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]

        self.clean_principal_frame()
        self.clean_canvas_frame()

        self.selected_images_indices = []
        self.segmentation = True

        self.contour = sc.contour_segmentation(self.img_tree.image)
        self.segmentated = sc.cluster_segmentation(
            self.img_tree.image, self.contour, sc.DEF_COLOR
        )

        self.update_screen()

        results = sc.generate_results(
            self.contour, self.height_mm / self.segmentated.shape[0]
        )
        self.fill_table(results, sc.DEF_COLOR)

    def segmentate(self) -> None:
        """
        This method is in charge of the shape segmentation at a cluster.
        """
        if len(self.selected_images_indices) > 1:
            tkinter.messagebox.showwarning(
                "Error", message="Por favor, seleccione solo una imagen."
            )
            return
        if len(self.selected_images_indices) == 1:
            self.img_tree = self.img_tree.childs[self.selected_images_indices[0]]

        self.clean_principal_frame()
        self.clean_canvas_frame()

        self.selected_images_indices = []
        self.segmentation = True

        self.contour = sc.contour_segmentation(self.img_tree.image)
        sc.contour_agrupation(self.contour)
        self.segmentated = sc.cluster_segmentation(
            self.img_tree.image, self.contour, sc.COLORS
        )

        self.update_screen()

        results = sc.generate_results(
            self.contour, self.height_mm / self.segmentated.shape[0]
        )
        self.fill_table(results, sc.COLORS)

    def aggregate(self, results) -> List:
        agg_results = []
        color_count = []
        # Results list initialization
        for i in range(len(sc.COLORS)):
            agg_results.append([])
            color_count.append(0)
            for _ in sc.STATISTICS_CM:
                agg_results[i].append(0)
        for res in results:
            color_count[res[0]] += 1
            for i in range(len(sc.STATISTICS_CM)):
                # i is the statistic to aggregate
                # i+1 is the position of the statistic
                # in the res list
                agg_results[res[0]][i] += res[i + 1]

        for i in range(len(agg_results)):
            if color_count[i] == 0:
                agg_results[i] = None
                continue
            for j in range(len(sc.STATISTICS_CM)):
                agg_results[i][j] /= color_count[i]
                agg_results[i][j] = np.round(agg_results[i][j], 2)
        return agg_results

    def create_label(self, name, row, col):
        label = ttk.Label(
            self.results_fr, text=name, style="Heading.TLabel", padding=(5, 6, 7, 8)
        )
        label.grid(row=row, column=col)
        return label

    def create_color_label(self, name, row, col):
        label = tkinter.Label(self.results_fr, text=name)
        label.grid(
            row=row, column=col, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )
        return label

    def fill_table(self, results, colors) -> None:
        """
        This method fills and shows a table at the GUI.
        The data is given as an input.
        """
        for widget in self.results_fr.winfo_children():
            widget.destroy()

        statistic_array = None
        unit = ""
        if self.cm:
            statistic_array = sc.STATISTICS_CM
            unit = "CM"
        else:
            statistic_array = sc.STATISTICS_MM
            unit = "MM"

        aggregated_results = self.aggregate(results)
        self.results_fr.grid(row=0, column=0, padx=10, pady=5)
        self.img_container_canvas.xview("moveto", 0)
        self.create_label("Color", 0, 0)
        self.create_label("Mineral", 0, 1)
        for i in range(len(statistic_array)):
            label = self.create_label(statistic_array[i], 0, i + 2)
            createBalloon(
                widget=label, header=statistic_array[i], text=sc.STATISTICS_DESC[i]
            )
        label = self.create_label("Area total (%)", 0, len(statistic_array) + 2)
        createBalloon(
            widget=label,
            header="Area total (%)",
            text="Indica el area total del mineral en relación al resto del testigo de roca.",
        )

        images = sc.image_agrupation(self.img_tree.image, self.contour, len(colors))

        for row_num in range(len(aggregated_results)):
            if aggregated_results[row_num] == None:
                continue
            (b, g, r) = colors[row_num]
            color = "#%02x%02x%02x" % (r, g, b)

            label_color = self.create_color_label("", row_num + 1, 0)
            label_color.config(bg=color, width=1, height=1, justify=tkinter.CENTER)
            name = PlaceholderEntry(self.results_fr, f"Mineral {row_num}")
            name.grid(row=row_num + 1, column=1, sticky=tkinter.W + tkinter.E)

            for col_num in range(len(statistic_array)):
                self.create_label(
                    aggregated_results[row_num][col_num], row_num + 1, col_num + 2
                )
            self.create_label(
                percent.percent(images[row_num]), row_num + 1, len(statistic_array) + 2
            )

        btn_export_name = "Descargar"
        btn_export_description = "Descarga los resultados obtenidos, guardando las estadisticas de cada figura en un archivo CSV y las fotos de los distintos minerales en un archivo zip"
        self.btn_export, self.hover_export = createButtonWithHover(
            self.results_fr,
            btn_export_name,
            lambda: self.table_to_csv(results, len(colors)),
            btn_export_description,
        )
        self.btn_export.grid(
            row=len(aggregated_results) + 1, column=len(statistic_array) // 2 + 1
        )

        btn_switch_unit_name = "Cambiar unidad"
        btn_switch_unit_description = (
            "Permite cambiar la unidad de medida entre centímetro o milímetros."
        )
        self.btn_switch_unit, self.hover_units = createButtonWithHover(
            self.results_fr,
            btn_switch_unit_name,
            self.switch_unit,
            btn_switch_unit_description,
            image=self.switch_btn_image,
        )
        self.btn_switch_unit.config(padding=0)
        self.btn_switch_unit.grid(
            row=len(aggregated_results) + 1, column=len(statistic_array) // 2 + 2
        )

        self.create_label(
            unit, len(aggregated_results) + 1, len(statistic_array) // 2 + 3
        )

    def table_to_csv(self, results, cluster_num) -> None:
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
        entrys = [
            wgets[i]
            for i in range(
                len(sc.STATISTICS_MM) + 4, len(wgets) - 3, len(sc.STATISTICS_MM) + 3
            )
        ]
        for entry in entrys:
            try:
                names.append(entry.get())
            except Exception as e:
                print(entry)
                print(e)
        header_row = ["Nombre Mineral", "ID imagen", *sc.STATISTICS_MM]
        with open(f"{filepath}_data.csv", "w", newline="") as f:
            wrtr = csv.writer(f, delimiter=",")
            wrtr.writerow(header_row)
            for i in range(len(results)):
                row = []
                row.append(names[results[i][0]])
                row.append(str(i))
                for j in range(len(sc.STATISTICS_MM)):
                    row.append(results[i][j + 1])
                wrtr.writerow(row)
        images = sc.image_agrupation(self.img_tree.image, self.contour, cluster_num)
        generate_zip(f"{filepath}_images", images)
        tkinter.messagebox.showinfo(
            "Guardado", message="Los resultados se han guardado correctamente"
        )

    def save(self) -> None:
        """
        This method saves both the current image and it's clusters if they exist.
        """
        files = [self.img_tree.image]
        files_names = [self.img_tree.name]

        for child in self.img_tree.childs:
            files.append(child.image)
            files_names.append(child.name)

        filepath = get_file_filepath()
        if not filepath:
            return

        generate_zip(filepath, files, files_names)
        tkinter.messagebox.showinfo(
            "Guardado", message="Las imagenes se han guardado correctamente"
        )

    def rotate_image(self) -> None:
        self.clean_principal_frame()
        self.rot_img = cv2.rotate(self.rot_img, cv2.ROTATE_90_CLOCKWISE)
        self.clone_img = self.rot_img
        self.sample_extractor.set_image(self._resize_img(self.rot_img), True)
        self.crop()

    def view_documentation(self) -> None:
        """
        This method open the documentation file. It opens de file that is save in the proyect or, if it fails,
        open the file that is save in the repository.
        """
        try:
            filepath = get_path("assets/Documentacion_Proyecto.pdf")
            webbrowser.open_new(filepath)
        except:
            webbrowser.open_new(
                "https://github.com/Lomolisso/geology-quantifier/blob/ba67360da5f0c7dc3e2edac6996fc463c8b78599/Documentacion_Proyecto.pdf"
            )

    def to_panoramic(self):
        self.sample_extractor.to_panoramic()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())

    def to_unwrapping(self):
        self.sample_extractor.to_unwrapping()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())

    def to_rectangle(self):
        self.sample_extractor.to_rectangle()
        self.sample_extractor.refresh_image()
        self.update_image(self.label_extractor, self.sample_extractor.get_image())

    def switch_unit(self) -> None:
        self.cm = not self.cm
        color_array = None
        if self.cm:
            self.switch_btn_image = ON
            self.height_mm *= 0.1
        else:
            self.switch_btn_image = OFF
            self.height_mm *= 10
        if self.toggle_var.get() == 1:
            color_array = sc.COLORS
        else:
            color_array = sc.DEF_COLOR

        results = sc.generate_results(
            self.contour, self.height_mm / self.segmentated.shape[0]
        )
        self.fill_table(results, color_array)


ROOT.title("Cuantificador geologico")
ROOT.wm_iconbitmap(get_path("./assets/icon.ico"))
ROOT.config(cursor="plus")
# Get user screen size

# Open window smaller than user screen
ROOT.geometry(f"{SCREEN_WIDTH * 19 // 20}x{SCREEN_HEIGHT * 17 // 20}+0+0")
# Set min and max window size to avoid incorrect displays
ROOT.minsize(SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT * 2 // 3)
ROOT.maxsize(SCREEN_WIDTH, SCREEN_HEIGHT)
gg = GUI(ROOT)

sv_ttk.set_theme("light")
ROOT.mainloop()
