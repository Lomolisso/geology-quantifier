"""
Utility functions/classes of the project.
"""


import tkinter as tk
from zipfile import ZipFile
import cv2
import sys
import os

class EntryWithPlaceholder(tk.Entry):
    """
    This class contains the behaviour of a new type of Entry
    for the GUI. It simplifies the handling of a placeholder.
    """

    def __init__(self, master=None, placeholder="PLACEHOLDER", color='black'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self) -> None:
        """
        Inserts a placeholder in the entry.
        """
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *_) -> None:
        """
        Handles when a user click the entry in order
        to fill it.
        """
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *_) -> None:
        """
        Handles when a use stops interacting with
        the entry.
        """
        if not self.get():
            self.put_placeholder()

def get_filepath() -> str:
    """
    Request the user to select where to store
    a file (or files)
    """
    filepath = tk.filedialog.askdirectory(
        initialdir=".",
        title='Elige donde guardar los resultados')
    return filepath

def generate_zip(filepath, files) -> None:
    """
    Generates a ZIP file that contains a list 
    of files given as an input.
    """
    zipObj = ZipFile(f'{filepath}.zip', 'w')
    i = 0
    for file in files:
        _, buf = cv2.imencode('.png', file)
        zipObj.writestr(str(i)+'.png', buf)
        i+=1

def get_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename