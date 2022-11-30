"""
This script contains different ways to load and save images.
All the loaded and saved images must be matrix objects.
"""

import cv2
import numpy as np
from tkinter import filedialog


def load_image_from_path(img_path: str) -> cv2.Mat:
    """
    Method to load an image usign the path declared by the user.
    """
    img = cv2.imread(img_path)
    try:
        assert img.size > 0
    except:
        return np.array([])
    return img

def save_image_from_path(img: cv2.Mat, img_path: str) -> None:
    """
    Method to save an image usign the path declared by the user.
    """
    if img_path == "":
        return False
    else:
        cv2.imwrite(f"{img_path}", img)
        return True

def load_image_from_window() -> None:
    """
    Method to load an image using OS file system UI.
    """

    # Ask for the image to load.
    filename = filedialog.askopenfilename(
        initialdir="../img",
        title="Select a File",
        filetypes=(
            ("Image files","*.png *.jpg *.tif"),
            ("all files", ".*")
        )
    )

    # Return the readed image as a matrix.
    img = cv2.imread(filename)
    try:
        assert img.size > 0
    except:
        return np.array([])
    return img, filename

def save_image_from_window(img: cv2.Mat) -> None:
    """
    Method to save an image using OS file system UI.
    """
    
    # Ask for the path where the image will be saved.
    filename = filedialog.asksaveasfilename(
        initialdir="../img",
        title="Save as",
        filetypes=(
            ("Image files","*.png *.jpg *.tif"),
            ("all files", ".*")
        )
    )

    if filename == "":
        return False
    else:
        # Save image using cv2 save method.
        # TODO get image type instead of hardcode the type.
        cv2.imwrite(f"{filename}.png", img)
        return True