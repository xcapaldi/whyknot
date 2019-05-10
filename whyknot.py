import tkinter as tk
import tkinter.filedialog as fd

# first we need to create a gui which will hold several components
# 1. a canvas to draw the knot in 2D
# 2. convert the drawing to a coordinate array
# 3. run coordinate array through pyknotid package to generate relevant code
# 4. save resulting data in csv

root = tk.Tk()
w = tk.Canvas(root, width=200, height=200)
w.pack()
w.create_line(0, 0, 200, 100)
w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
w.create_rectangle(50, 25, 150, 75, fill="blue")

root.filename = fd.asksaveasfilename(initialdir="/", title="Select File")
print(root.filename)

root.mainloop()
