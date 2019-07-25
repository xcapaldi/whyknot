#  WhyKnot
#  Graphical wrapper for PyKnotID package
#  Xavier and Luc Capaldi

# import modules
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import numpy as np
import pyknotid
import pyknotid.spacecurves as pkidsc
import sympy
import csv
import os

# set initial values
x0, y0 = 0, 0
gc_str = ""
fileopen = False
t = sympy.Symbol('t') # for use in displaying polynomial invariant

#  Set line/node graphical defaults
linewidth = 2
linecolor = "#a3be8c"
noderadius = 5
nodecolor = "#bf616a"
bridgewidth = 3
background_color = "#d9d9d9"

# determine equation of line
def defineline(x1,y1,x2,y2):
    xbound = [x1,x2]
    ybound = [y1,y2]
    if x1 == x2:
        slope = None
    else:
        slope = (y2-y1)/(x2-x1)
    return xbound, ybound, slope

# find the y-intercept of a given line
def findyintercept(x,y,m):
    b = y - (m * x)
    return b


# check if two lines intersect
def checkintersect(xbound1,xbound2,ybound1,ybound2,slope1,slope2):
    # check if we have overlap in x range first
    if max(xbound1) > min(xbound2) or max(xbound2) > min(xbound1):
        # then check if we have overlap in y range
        if max(ybound1) > min(ybound2) or max(ybound2) > min(ybound1):
           # then check if line 1 is vertical
           if slope1 == None:
               # in this case, the two lines intersect everywhere
               if slope2 == None:
                   # technically not correct but for the purposes of this script it will
                   # suffice
                   return None 
               # otherwise, only line 1 is vertical
               else:
                   b2=findyintercept(xbound2[0],ybound2[0],slope2)
                   xintersect = xbound1[0]
                   yintersect = slope2 * xintersect + b2
                   return xintersect, yintersect
           elif slope2 == None:
               # the previous conditional already checked if line 1 was vertical
               b1=findyintercept(xbound1[0],ybound1[0],slope1)
               xintersect = xbound2[0]
               yintersect = slope1 * xintersect + b1
               return xintersect, yintersect
           # if neither line is vertical
           else:
               b1=findyintercept(xbound1[0],ybound1[0],slope1)
               b2=findyintercept(xbound2[0],ybound2[0],slope2)
               xintersect = (b2-b1)/(slope1-slope2)
               yintersect = slope1 * xintersect + b1
               return xintersect, yintersect
        else:
            return None # outside y range
    else:
        return None # outside x range

# determine which lines to check for intersection
# this function ignores the end point of the lines which is good for our purposes
# I am not sure if this is computationally more efficient than just checking for
# intersections with every line
def potentialintersection(xbound,ybound,linearray):
    # take the bounds of one line and the bounds of the other lines stored in an array
    # define bounding box
    left = min(xbound)
    right = max(xbound)
    bottom = min(ybound)
    top = max(ybound)
    # empty array to store lines with potential intersections
    potintersections = []
    # each element of linearray is a list which contains the xbounds, ybounds and slope
    for line in linearray:
        xmin = min(line[0])
        xmax = max(line[0])
        ymin = min(line[1])
        ymax = max(line[1])
        # check if the line is in the bounding box at all
        if (xmax > left and xmax < right) or (xmin > left and xmin < right):
            if (ymax > bottom and ymax < top) or (ymin > bottom and ymin < top):
                potintersections.append(line)
    return potintersections


# define bounds of bridge
def definebridge(xintersect,yintersect,slope,bridgewidth,bridgeheight):
    # slope represents the top line
    halfbridge = bridgewidth/2
    # if top line is vertical
    if slope == None:
        x = 0
        y = halfbridge
    # else if top line has an angle from vertical
    else:
        # find angle from slope
        angle = np.arctan(slope)
        x = halfbridge*np.cos(angle)
        y = halfbridge*np.sin(angle)
    bridge=[[xintersect-x,xintersect+x],[yintersect-y,yintersect+y],bridgeheight]
    return bridge

#  Draw new lines and nodes based on mouse click event
def drawline(event):
    global x0, y0, node_counter, line_counter
    intersect = False
    closure = False
    x, y = event.x, event.y

    #  Hitbox variable to change crossroad intersect
    hb = 20
    #  Check if user clicks on any intersects along normal lines
    for coord in intersect_coords:
        #  Create hitbox for over/under intersection switching
        x_low, x_high = int(coord[0] - hb), int(coord[0] + hb)
        y_low, y_high = int(coord[1] - hb), int(coord[1] + hb)
        if x > x_low and x < x_high and y > y_low and y < y_high:
            intersect = True
            #  Store which intersection is clicked
            local_intersect = coord
    #  Check if user clicks on any interersects along closure line
    for coord in closure_intersects:
        #  Create hitbox for over/under intersection switching
        x_low, x_high = int(coord[0] - hb), int(coord[0] + hb)
        y_low, y_high = int(coord[1] - hb), int(coord[1] + hb)
        if x > x_low and x < x_high and y > y_low and y < y_high:
            intersect = True
            closure = True
            #  Store which intersection is clicked
            local_intersect = coord
    if intersect == False:
        #  Generate naming convention for tags
        node_tag = "node_" + str(node_counter)
        line_tag = "line_" + str(line_counter)

        if x0 == 0 & y0 == 0:
            draw.create_oval(
                x - noderadius,
                y - noderadius,
                x + noderadius,
                y + noderadius,
                fill=nodecolor,
                width=0,
                tags=node_tag,
            )
            node_counter += 1
        else:
            draw.create_line(
                x0, y0, x, y, fill=linecolor, width=linewidth, tags=line_tag
            )
            draw.create_oval(
                x - noderadius,
                y - noderadius,
                x + noderadius,
                y + noderadius,
                fill=nodecolor,
                width=0,
                tags=node_tag,
            )
            node_counter += 1
            line_counter += 1

        x0, y0 = x, y

        #  Record info about line and find intersections
        record_line_info(x, y)
        if len(node_coords) > 1:
            line_intersects = calculate_intersect_coords(line_start_coords[-1][0],
                                                         line_end_coords[-1][0],
                                                         line_m[-1],
                                                         b1 = line_b[-1])
            for i in line_intersects:
                #  Add coordinates (key) and reference index values to
                #  dictionary
                #  i = [x,y, line_num_bot, line_num_top]
                intersect_node_dict[(i[0], i[1])] = i[2], i[3]
                intersect_coords.append([i[0], i[1]])
                #  Update intersections visually
                create_intersections(i[0], i[1])
    else:
        x_intersect = local_intersect[0]
        y_intersect = local_intersect[1]
        if closure == True:
            update_crossroads(x_intersect, y_intersect, closure=True)
        else:
            update_crossroads(x_intersect, y_intersect)

#  Calculate gauss code, alexander polynomial, determinant, 2nd and 3rd degree vassiliev
#  invariants and updates the label
def find_gc(event):
    global gc
    global k
    if len(node_coords) > 1:
        #  Convert to array
        node_coords_array = np.asarray(node_coords)
        k = pkidsc.Knot(node_coords_array)
        gc = k.gauss_code()
        # simplify the gauss code
        gc.simplify()
        g_code.config(text=str(gc))

#  Clear all data and objects on canvas
def clear_canvas(event):
    global x0, y0, node_coords, line_start_coords, line_end_coords, line_m
    global line_b, intersect_coords, intersect_node_dict, knot_coords
    global node_counter, line_counter, intersected_list
    draw.delete("all")
    x0, y0 = 0, 0
    node_coords.clear()
    knot_coords.clear()
    line_start_coords.clear()
    line_end_coords.clear()
    line_m.clear()
    line_b.clear()
    intersect_coords.clear()
    intersect_node_dict.clear()
    analysis_results.clear()
    g_code.config(text="--")
    clos_var.set(0)
    node_counter = 0
    line_counter = 0
    intersect_stack_dict.clear()
    tag_dict.clear()
    intersect_crossroads.clear()
    crossroad_start_end.clear()
    closure_line_info.clear()
    closure_intersects.clear()
    intersected_list.clear()

def display_coords_realtime(event):
    x, y = event.x, event.y
    coords = str(x) + ", " + str(y)
    coords_realtime.config(text=coords)

# create function to close program
def close_window():
    window.destroy()

# clear clipboard and copy the currently displayed gauss code
def copy_gauss(event):
    root.clipboard_clear()
    root.clipboard_append(gc_str)

# open file to save data
def open_file(event):
    global numknots
    global fileopen
    # set number of entries to -1 initially so we don't count the header
    numknots = -1
    root.filename = fd.askopenfilename(initialdir = "/", title = "Select file",filetypes=[("comma-separated values",".csv")])
    filename.config(text=root.filename.split("/")[-1])
    fileopen = True
    # update numknots NEEDS TESTING
    with  open(root.filename, newline='') as csvfile:
        knotentries = csv.reader(csvfile, delimiter = ' ', quotechar="|")
        for row in knotentries:
            numknots+=1
    entries.config(text=str(numknots)+" entries")

# new file to save data to
def new_file(event):
    global numknots
    global fileopen
    # ask for new filename and location
    root.filename = fd.asksaveasfilename(initialdir = "/", title = "New file",
    defaultextension=".csv")
    # make file
    with open(root.filename,'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["gauss","crossingnum","alexander"])
    # update filename
    filename.config(text=root.filename.split("/")[-1])
    fileopen = True
    # set number of knots to 0
    numknots = 0

def write_data(event):
    global numknots
    if fileopen == True:
        # update number of knots
        numknots=numknots+1
        entries.config(text=str(numknots)+" entries")
        # check if knot directory exists and creates it if not
        jsonpath = root.filename[:-4]+"_json"
        if os.path.exists(jsonpath)!=True:
            os.makedirs(jsonpath)
        # save knot coordinate data to json file
        k.to_json(jsonpath+"/"+str(numknots)+".json")
        # write knot analysis to csv
        with open(root.filename,'a') as f:
            writer = csv.writer(f)
            writer.writerow([str(gc),len(gc),str(k.alexander_polynomial(variable=t))])
    else:
        mb.showerror("Error", "No active file. Open a file or start a new file to save data.")
    
def popuphelp(event):
    mb.showinfo("Help", "A wrapper which allows graphical input of knots to be analyzed with pyknotid.\nYou can open a previous csv file or start a new one and then draw your knot. The closure option doesn't change the analysis. It only affects the appearance. Upon saving (w), the knot coordinates are saved as a json file in a subfolder created by the program in the working directory. The analysis details are also appended to the csv. The canvas can be cleared (c) and the program can be closed easily (q).\nCreated by Xavier and Luc Capaldi and released with the MIT License (c) 2019. ")

def popupmoo(event):
    mb.showwarning("Moo", "    -----------\n< whyknot >\n    -----------\n        \   ^__^\n         \  (oo)\_______\n            (__)\           )\/\ \n                  ||-----w |\n                  ||        ||")

#  Create GUI
root = tk.Tk()
root.title("WhyKnot")

#  Create main frames within the root frame
draw_frame = tk.Frame(root)
interface_frame = tk.Frame(root, width=300, height=800)

#  Set geometry manager class for main frames
draw_frame.grid(column=0, row=0)
interface_frame.grid(column=1, row=0)
# interface_frame.grid_propagate(False)   #  widgets expand frame

#  Organize main frames within the root frame
draw_frame.grid(column=0, sticky="nsw")
interface_frame.grid(column=1, sticky="nse")

#  Create canvas widget for draw frame
draw = tk.Canvas(draw_frame, width=600, height=800)

#  Place widget in draw frame
draw.grid(row=0, column=0)

#  Create widgets for right (interface) frame
title = tk.Label(interface_frame, text="WhyKnot", font=("Helvetica", 18))

g_code_var = tk.StringVar()  #  Button var so text can be updated
g_code_var.set("--")
g_code = tk.Label(interface_frame, text="--", font=("Helvetica", 15), wraplength=300)

clos_var = tk.IntVar()
closures = tk.Checkbutton(interface_frame, text="Include closure", variable=clos_var)

file = tk.Button(interface_frame, text="File")
new = tk.Button(interface_frame, text="New")
save = tk.Button(interface_frame, text="Save (w)")
help = tk.Button(interface_frame, text="Help")
# results = tk.Label(interface_frame, text="Results Goes Here")
close = tk.Button(interface_frame, text="Quit (q)")
clear = tk.Button(interface_frame, text="Clear (c)")
coords_realtime = tk.Label(interface_frame, text="--")
filename = tk.Label(interface_frame, text="no file", font=("Helvetica",10))
entries = tk.Label(interface_frame, text="0 entries", font=("Helvetica",10))

#  Place widgets in interface frame
title.grid(row=0, columnspan=2)
g_code.grid(row=6, columnspan=2)
closures.grid(row=5, columnspan=2)
file.grid(row=1, column=0)
new.grid(row=1, column=1)
save.grid(row=2, column=0)
help.grid(row=2, column=1)
filename.grid(row=3, columnspan=2)
entries.grid(row=4, columnspan=2)
clear.grid(row=7, column=0)
close.grid(row=7, column=1)
coords_realtime.grid(row=9, columnspan=2)

#  Initialize event handler
draw.bind("<Button-1>", drawline, add="+")
draw.bind("<Button-1>", find_gc, add="+")
clear.bind("<Button-1>", clear_canvas)
root.bind("c", clear_canvas)
close.bind("<Button-1>", lambda e: root.destroy())
root.bind("q", lambda e: root.destroy())
closures.bind("<Button-1>", include_closures)
#closures.bind("<Button-1>", find_gc)
draw.bind("<Motion>", display_coords_realtime)
root.bind("y", copy_gauss)
save.bind("<Button-1>", write_data)
help.bind("<Button-1>", popuphelp)
root.bind("w", write_data)
file.bind("<Button-1>",open_file)
new.bind("<Button-1>",new_file)
root.bind("m", popupmoo)

root.mainloop()
