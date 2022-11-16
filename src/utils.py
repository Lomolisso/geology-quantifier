"""
Utility functions/classes of the project.
"""


import tkinter
from tkinter import ttk
from zipfile import ZipFile
import cv2
import sys
import os
from ttkwidgets.frames import Balloon
# import Pmw

# def init_pmw(root):
#     Pmw.initialise(root) #initializing it in the root window

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.field_style = kwargs.pop("style", "TEntry")
        self.placeholder_style = kwargs.pop("placeholder_style", self.field_style)
        self["style"] = self.placeholder_style

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.field_style

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style



def createBalloon(widget, button_name, text):
    """
    Creates a Balloon object to display a description of the widget.
    The description is displayed after 1 second.
    """
    width = 200
    timeout = 1
    return Balloon(master=widget, headertext=button_name, text=text, timeout=timeout, width=width)

def createButtonWithHover(master, name, command, description, image=None):
    """
    Creates a new button with a hover balloon.
    """
    width = 20
    cursor = 'arrow'
    btn = ttk.Button(master=master, text=name, width=width, command=command, cursor=cursor, image=image)
    hover = createBalloon(btn, name, description)
    return btn, hover

def get_results_filepath() -> str:
    """
    Request the user to select where to store
    the results and with which name
    """
    filepath = tkinter.filedialog.asksaveasfilename(
        initialdir=".",
        title="Elige donde guardar los resultados",
        filetypes=(
            ("all files", ".*"),
            ('Zip File', '*.zip'),
            ('CSV File', '*.csv')
        )
    )
    return filepath

def get_file_filepath() -> str:
    """
    Request the user to select where to store
    a file and with which name
    """
    filepath = tkinter.filedialog.asksaveasfilename(
        initialdir="../img",
        title="Guardar como",
        filetypes=(
            ('Zip File', '*.zip'),
            ("all files", ".*")
        )
    )
    return filepath

def generate_zip(filepath, files, files_name=None) -> None:
    """
    Generates a ZIP file that contains a list 
    of files given as an input.
    """
    if not files_name:
        files_name = range(len(files))
        files_name = map(str, files_name)
    zipObj = ZipFile(f'{filepath}.zip', 'w')
    for (file_img, name) in zip(files, files_name):
        _, buf = cv2.imencode('.png', file_img)
        zipObj.writestr(name + '.png', buf)

def get_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename