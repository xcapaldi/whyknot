#  WhyKnot
#  Graphical wrapper for PyKnotID package

import tkinter as tk
import tkinter.filedialog as fd
from sympy import Point, Line, Segment
from scipy.optimize import fsolve
import numpy as np
import pyknotid
from pyknotid.spacecurves import Knot
import pyknotid.spacecurves as pkidsc
from math import pi, exp
from cmath import sqrt

# set initial point
x0, y0 = 0, 0

#  Set line/node defaults
linewidth = 2
linecolor = "#a3be8c"
noderadius = 5
nodecolor = "#bf616a"

#  Create lists to store variables
node_coords = []
line_start_coords = []
line_end_coords = []
line_m = []
line_b = []
intersect_coords = []
intersect_node_dict = {}
analysis_results = []  #  Order of items in results: Crossing number,
                       #  Determinant|Δ(-1)|, |Δ(exp(2πi/3)|, |Δ(i)|,
                       #  Vassiliev order 2 (v2), Vassiliev order 3 (v3)

#  Calculate possible intersects based on (input) test line
def find_possible_intersects(test_line):
    #  List to store x coords
    line_info = []
    #  Collect points and put in correct order
    p1, p2, p3, p4 = test_line[0], test_line[1]+1, test_line[0], test_line[1]+1
    if p2 > p1:
        p1,p2 = p2,p1
    if p4 > p3:
        p3,p4 = p4,p3
    #  Iterate through every other line
    counter = 0
    for coord_start, coord_end in zip(line_start_coords[:-2],
                                      line_end_coords[:-2]):
        I2 = [coord_start[0], coord_end[0]]
        #  Calculate x coord of potential intersection
        m1 = line_m[-1]
        b1 = line_b[-1]
        m2 = line_m[counter]
        b2 = line_b[counter]
        counter += 1
        x = int((b2 - b1) / (m1 - m2))
        line_info.append([x, counter, m1, b1, m2, b2])
    return line_info, p1, p2, p3, p4

#  Find all intersects for current (newest) line segment
def calculate_intersect_coords():
    global intersect_coords, intersect_node_dict
    if len(node_coords) > 3:
        #  Range for test line
        I1 = [line_start_coords[-1][0], line_end_coords[-1][0]]
        line_info, p1, p2, p3, p4 = find_possible_intersects(I1)
        for line in line_info:
            x = line[0]
            m1 = line[2]
            b1 = line[3]
            m2 = line[4]
            b2 = line[5]
            #  Verify coord is an intersection
            if x < p1 and x > p2 and x < p3 and x > p4:
                y = int((m1 * x) + b1)
                #  Add coordinates and reference value to dictionary
                intersect_node_dict[(x,y)] = (line[1]-1)
                intersect_coords.append([x,y])

#  Find slope of given line from two points
def find_slope(p1, p2):
    #  (y2 - y1) / (x2 - x1)
    try:
        slope = ((p2[1] - p1[1]) / (p2[0] - p1[0]))
    except ZeroDivisionError:
        print("Error! Division by zero.")
    return slope

#  Find y-intercept of given line from two points and slope
def find_y_intercept(p1, slope):
    #  b = y - mx
    return p1[1] - (slope * p1[0])

#  Record line information in arrays
def record_line_info(x,y):
    global node_coords, line_start_coords, line_end_coords, line_m, line_b
    #  Calculate/record coordinate and line information
    index = -1
    node_coords.append([y,x,0])
    if len(node_coords) > 1:
        line_start_coord_value = node_coords[index-1][0:2]
        line_start_coords.append(line_start_coord_value)
        line_end_coord_value = node_coords[index][0:2]
        line_end_coords.append(line_end_coord_value)
        line_m_value = find_slope(line_start_coords[-1], line_end_coords[-1])
        line_m.append(line_m_value)
        line_b_value = find_y_intercept(line_start_coords[-1], line_m[-1])
        line_b.append(line_b_value)
        index -=1

#  Obtain tags from intersect coordinates and modify z-values of node
#  coordinate array accordingly
def modify_z_values():
    global node_coords
    for coord in intersect_coords:
        x,y = coord[0],coord[1]
        try:
            intersect_num = intersect_node_dict[(x,y)]
            node_coords[-1][2] = 1
            node_coords[intersect_num][2] = -1
        except KeyError:
            continue

#  Draw new lines and nodes based on mouse click event
def drawline(event):
    global x0, y0
    #  Generate naming convention for tags
    node_tag = ("node_" + str(len(node_coords)))
    line_tag = ("line_" + str(len(node_coords)))
    #  Create nodes and lines, assign tags
    x, y = event.x, event.y
    if x0 == 0 & y0 == 0:
        draw.create_oval(
            x - noderadius,
            y - noderadius,
            x + noderadius,
            y + noderadius,
            fill=nodecolor,
            width=0,
            tags=node_tag
        )
    else:
        draw.create_line(x0, y0, x, y, fill=linecolor,
                         width=linewidth, tags=line_tag)
        draw.create_oval(
            x - noderadius,
            y - noderadius,
            x + noderadius,
            y + noderadius,
            fill=nodecolor,
            width=0,
            tags=node_tag
        )
    x0, y0 = x, y
    record_line_info(x,y)
    calculate_intersect_coords()
    modify_z_values()

#  Calculate gauss code and update label
def find_gc(event):
    if len(node_coords) > 1:
        #  Convert to array
        node_coords_array = np.asarray(node_coords)
        #  Calculate gauss code
        closures = clos_var.get()  #Returns opposite of current button state
        if closures == 0:
            gc = (pkidsc.spacecurve.SpaceCurve(node_coords_array,
                  verbose=False).gauss_code(include_closure=False))
        else:
            gc = (pkidsc.spacecurve.SpaceCurve(node_coords_array,
                 verbose=False).gauss_code())
        gc_str = str(gc)
        g_code.config(text=gc_str)                   

#  Placehold for button functionality
def button_placeholder():
    print("Hello world")

#  Clear all data and objects on canvas
def clear_canvas(event):
    global x0, y0, node_coords, line_start_coords, line_end_coords, line_m
    global line_b, intersect_coords, intersect_node_dict
    draw.delete("all")
    x0, y0 = 0, 0
    node_coords = []
    line_start_coords = []
    line_end_coords = []
    line_m = []
    line_b = []
    intersect_coords = []
    intersect_node_dict.clear()
    analysis_results = []
    g_code.config(text="--")

#  Visually add or remove the closure line segment
def include_closure(event):
    closures = clos_var.get()  #Returns opposite of current button state
    if len(node_coords) >= 3:
        if closures == 0:
            x1, y1 = node_coords[0][1], node_coords[0][0]
            x2, y2 = node_coords[-1][1], node_coords[-1][0]
            draw.create_line(x1, y1, x2, y2, fill=linecolor,
                             width=linewidth, tags="closure")
        else:
            draw.delete("closure")
            
#  Find number of total intersections
def find_crossing_number():
    #  Find the number of intersections for the closure line
    num_closure_intersects = 0
    if len(node_coords) > 1:
        closures = clos_var.get()
        if closures == 0:
            x1, x2 = node_coords[0][1], node_coords[-1][1]
            line_info, p1, p2, p3, p4  = find_possible_intersects([x1,x2])
            for line in line_info:
                x = line[0]
                #  Verify coord is an intersection
                if x < p1 and x > p2 and x < p3 and x > p4:
                    num_closure_intersects += 1
    crossing_num = len(intersect_coords) + num_closure_intersects
    return crossing_num
    
###  Perform and store analysis based on drawn knot
##def perform_analysis():
##    global analysis_results
##    if len(intersect_coords) > 0:
##        crossing_num = find_crossing_number()
##        #  'Reduced crossing number' is excluded because unknown and is never
##        #  assigned a value on the online module.
##        #  Determinant|Δ(-1)| - Alexander polynomial evaluated at -1
##        node_coords_array = np.asarray(node_coords)
##        determinant = (pkidsc.knot.Knot(node_coords_array,
##                       verbose=False).determinant())
##        #  |Δ(exp(2πi/3)| - Alexander polynomial evaluated at 2πi/3
##        alexander_1 = (pkidsc.knot.Knot.alexander_at_root(2*pi*1j)/3,
##                       round=True))
##        #  |Δ(i)| - Alexander polynomial evaluated at i
##        alexander_2= pkidsc.knot.Knot.alexander_at_root(1j, round=True)
##        #  Vassiliev invariant order 2, v2
##        vassiliev_order2 = (pyknotid.invariants.
#                             vassiliev_degree_2(intersect_coords))
##        #  Vassiliev invariant order 3, v3
##        vassiliev_order3 = (pyknotid.invariants.
##                            vassiliev_degree_3(intersect_coords))
##        #  Store results of analysis
##        analysis_results.extend((crossing_num, determinant, alexander_1,
##                                 alexander_2, vassiliev_order2,
#                                  vassiliev_order3))
    

#  Create GUI
root = tk.Tk()
root.title("WhyKnot")
    
#  Create main frames within the root frame
draw_frame = tk.Frame(root)
interface_frame = tk.Frame(root, width = 300, height = 800)

#  Set geometry manager class for main frames
draw_frame.grid(column=0, row=0)
interface_frame.grid(column=1, row=0)
#interface_frame.grid_propagate(False)   #  widgets expand frame

#  Organize main frames within the root frame
draw_frame.grid(column=0, sticky='nsw')
interface_frame.grid(column=1, sticky='nse')

#  Create canvas widget for draw frame
draw = tk.Canvas(draw_frame, width=800, height=800)

#  Place widget in draw frame
draw.grid(row=0, column=0)

#  Create widgets for right (interface) frame
title = tk.Label(interface_frame, text="WhyKnot", font=('Helvetica', 18))

g_code_var = tk.StringVar()  #  Button var so text can be updated
g_code_var.set("--")
g_code = tk.Label(interface_frame, text="--", font=('Helvetica', 15),
                  wraplength=300)

clos_var = tk.IntVar()
closures = tk.Checkbutton(interface_frame, text = "Include Closures?",
                          variable = clos_var)
file = tk.Button(interface_frame, text=" File ")#, command=button_placeholder)
save = tk.Button(interface_frame, text="Save")#, command=button_placeholder)
results = tk.Label(interface_frame, text = "Results Goes Here")
analyze = tk.Button(interface_frame, text="Analyze")
clear = tk.Button(interface_frame, text="Clear")

#  Place widgets in interface frame
title.grid(row=0, columnspan=2)
g_code.grid(row=3, columnspan=2)
closures.grid(row=2, columnspan=2)
file.grid(row=1, column=0)
save.grid(row=1, column=1)
analyze.grid(row=4, column=0)
results.grid(row=6, columnspan=2)
clear.grid(row=4, column=1) 

#  Initialize event handler
draw.bind("<Button-1>", drawline)
clear.bind("<Button-1>", clear_canvas)
analyze.bind("<Button-1>", find_gc)
closures.bind("<Button-1>", include_closure)
root.mainloop()
