"""
Utility functions/classes of the project.
"""


import os
import sys
import tkinter
from tkinter import ttk
from zipfile import ZipFile

import cv2
from ttkwidgets.frames import Balloon


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
        """
        Deletes the actual placeholder of the entry.
        """
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.field_style

    def _add_placeholder(self, e):
        """
        Set the original placeholder of the entry.
        """
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style


def createBalloon(widget, header, text):
    """
    Creates a Balloon object to display a description of the widget.
    The description is displayed after 1 second.
    """
    width = 200
    timeout = 1
    return Balloon(
        master=widget, headertext=header, text=text, timeout=timeout, width=width
    )


def createButtonWithHover(master, name, command, description, image=None):
    """
    Creates a new button with a hover balloon.
    """
    width = 20
    cursor = "arrow"
    btn = ttk.Button(
        master=master,
        text=name,
        width=width,
        command=command,
        cursor=cursor,
        image=image,
    )
    hover = createBalloon(btn, name, description)
    return btn, hover


def createCheckBoxWithHover(master, name, description, variable, text="", command = None):
    """
    Creates a new checkbox with a hover balloon.
    """
    width = 20
    cursor = "arrow"
    switch = ttk.Checkbutton(
        master=master,
        width=width,
        text=text,
        cursor=cursor,
        style="Switch.TCheckbutton",
        variable=variable,
        command=command,
    )
    hover = createBalloon(switch, name, description)
    return switch, hover


def get_results_filepath() -> str:
    """
    Request the user to select where to store
    the results and with which name
    """
    filepath = tkinter.filedialog.asksaveasfilename(
        initialdir=".",
        title="Elige donde guardar los resultados",
        filetypes=(("all files", ".*"), ("Zip File", "*.zip"), ("CSV File", "*.csv")),
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
        filetypes=(("Zip File", "*.zip"), ("all files", ".*")),
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
    zipObj = ZipFile(f"{filepath}.zip", "w")
    for (file_img, name) in zip(files, files_name):
        _, buf = cv2.imencode(".png", file_img)
        zipObj.writestr(name + ".png", buf)


def get_path(filename):
    """
    Returns the absolute path of a given filename.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return os.path.abspath(filename)
