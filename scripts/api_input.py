from PIL import ImageTk, Image
from tkinter import filedialog, mainloop
import tkinter
import cv2


root = tkinter.Tk()
root.withdraw()
# root.title("Image viewer")
# root.iconbitmap('c:/prueba/cart.ico')

filename = filedialog.askopenfilename(initialdir="./img", title="Select a File", filetypes=(("png files","*.png"), ("all files", ".*")))
root.withdraw()

img = cv2.imread(filename)
cv2.imshow("Testigo",img)
cv2.waitKey(0)
