import tkinter as tk
from tkinter import ttk
from tkinter import *

root = tk.Tk()
container = ttk.Frame(root)
container2 = ttk.Frame(root)
canvas2 = tk.Canvas(container2, bg='blue',width=400, height=400)
canvas = tk.Canvas(container)
canvas2.grid()
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)




canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

container.columnconfigure(0, weight=1)
container.rowconfigure(0, weight=1)

canvas.configure(yscrollcommand=scrollbar.set)

for i in range(50):
    a=tk.Canvas(scrollable_frame,width=400, height=400)
    label1 = tk.Label(a, bg='blue', height=20, width=50)
    label2 = tk.Label(a, bg='red', height=20, width=50)
    label2.grid(row = 0, column = 0, padx=20, pady=20)
    label1.grid(row = 0, column = 1, padx=20, pady=20)

    a.grid()

container2.grid(row=0, column=1)
container.grid(row=0,column=0,sticky=W+N+E+S)
canvas.grid(row=0, column=0,sticky=W+N+E+S)
scrollbar.grid(row=0, column=1,sticky=N+S)

root.mainloop()
