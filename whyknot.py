import tkinter as tk
import tkinter.filedialog as fd

root = tk.Tk()
w = tk.Canvas(root, width=200, height=200)
w.pack()
w.create_line(0,0,200,100)
w.create_line(0,100,200,0,fill="red",dash=(4,4))
w.create_rectangle(50,25,150,75,fill="blue")

root.filename = fd.asksaveasfilename(initialdir = "/",title="Select File")
print(root.filename)

root.mainloop()
