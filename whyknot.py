import tkinter as tk
import tkinter.filedialog as fd

# first we need to create a gui which will hold several components
# 1. a canvas to draw the knot in 2D
# - fit into grid with buttons and output
# - show intersections?
# - show depth?
# - ability to modify intersections
# 2. convert the drawing to a coordinate array
# noderadius. run coordinate array through pyknotid package to generate relevant code
# 4. save resulting data in csv

# set initial point
x0, y0 = 0, 0

linewidth = 2
linecolor = "#a3be8c"
noderadius = 5
nodecolor = "#bf616a"


def drawline(event):
    x, y = event.x, event.y
    global x0, y0
    if x0 == 0 & y0 == 0:
        d.create_oval(
            x - noderadius,
            y - noderadius,
            x + noderadius,
            y + noderadius,
            fill=nodecolor,
            width=0,
        )
    else:
        d.create_line(x0, y0, x, y, fill=linecolor, width=linewidth)
        d.create_oval(
            x - noderadius,
            y - noderadius,
            x + noderadius,
            y + noderadius,
            fill=nodecolor,
            width=0,
        )
    x0, y0 = x, y
    return


# need to think about levels...
# https://www.geeksforgeeks.org/given-a-set-of-line-segments-find-if-any-two-segments-intersect/

root = tk.Tk()
d = tk.Canvas(root, width=800, height=800)
d.pack()

root.bind("<Button-1>", drawline)
# root.filename = fd.asksaveasfilename(initialdir="/", title="Select File")
# print(root.filename)

root.mainloop()
