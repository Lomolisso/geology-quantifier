"""
Api for easy file management
"""
import tkinter, cv2
from tkinter import filedialog

# Create tk object and hide tk window.
root = tkinter.Tk()
root.withdraw()

def load_image():
    """
    Method to load image from a selected path, using windows file system UI.
    """
    # Ask for the image to load.
    filename = filedialog.askopenfilename(initialdir="../img", title="Select a File", filetypes=(("Image files","*.png *.jpg"), ("all files", ".*")))
    root.withdraw()
    print(f"Loading image with name: {filename}")
    # Return the readed image as a matrix.
    return cv2.imread(filename)

def save_image(img):
    """
    Method to save image from a selected path, using windows file system UI.
    """
    # Ask for the path where the image will be saved.
    filename = filedialog.asksaveasfilename(initialdir="../img", title="Select a File", filetypes=(("Image files","*.png *.jpg"), ("all files", ".*")))
    root.withdraw()
    # Save image using cv2 save method.
    # TODO get image type besides hardcode the type.
    if filename == "":
        return False
    else:
        print(f"Saving image with name: {filename}")
        cv2.imwrite(f"{filename}.png", img)
        return True
