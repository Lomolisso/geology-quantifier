"""
This script contains different ways to load and save images.
All the loaded and saved images must be matrix objects.
"""

import tkinter, cv2
from tkinter import filedialog

# String to identify the prints of this file
TOKEN = "[IMG_MAN]"

# Global vars for interactive file system UI.
root = tkinter.Tk()
root.withdraw()

def load_image_from_path(img_path):
    """
    Method to load an image usign the path declared by the user.
    """
    return cv2.imread(img_path)

def save_image_from_path(img, img_path):
    """
    Method to save an image usign the path declared by the user.
    """
    if img_path == "":
        return False
    else:
        cv2.imwrite(f"{img_path}", img)
        return True

def load_image_from_window():
    """
    Method to load an image using OS file system UI.
    """
    # Ask for the image to load.
    filename = filedialog.askopenfilename(initialdir="../img", title="Select a File", filetypes=(("Image files","*.png *.jpg"), ("all files", ".*")))
    root.withdraw()
    print(f"{TOKEN} Loading image with name: {filename}")
    # Return the readed image as a matrix.
    return cv2.imread(filename)

def save_image_from_window(img):
    """
    Method to save an image using OS file system UI.
    """
    # Ask for the path where the image will be saved.
    filename = filedialog.asksaveasfilename(initialdir="../img", title="Save as", filetypes=(("Image files","*.png *.jpg"), ("all files", ".*")))
    root.withdraw()
    if filename == "":
        return False
    else:
        # Save image using cv2 save method.
        print(f"{TOKEN} Saving image with name: {filename}")
        # TODO get image type instead of hardcode the type.
        cv2.imwrite(f"{filename}.png", img)
        return True