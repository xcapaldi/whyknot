#  WhyKnot
#  Graphical wrapper for PyKnotID package
#  Xavier and Luc Capaldi


import tkinter as tk
import tkinter.filedialog as fd
import numpy as np
import pyknotid
import pyknotid.spacecurves as pkidsc
from sympy import Symbol, exp, I, pi

# set initial point
x0, y0 = 0, 0

gc_str = ""

#  Set line/node defaults
linewidth = 2
linecolor = "#a3be8c"
noderadius = 5
nodecolor = "#bf616a"
background_color = "#d9d9d9"

#  Create lists to store variables
node_coords = []
line_start_coords = []
line_end_coords = []
line_m = []
line_b = []
intersect_coords = []

#  Key: intersect coordinates
#  Value: index number of line being intersected, line intersecting
intersect_node_dict = {}
analysis_results = []  #  Order of items in results: Crossing number,
#  Determinant|Δ(-1)|, |Δ(exp(2πi/3)|, |Δ(i)|,
#  Vassiliev order 2 (v2), Vassiliev order 3 (v3)

intersect_stack_dict = {}  #  Stores which line is on top/bottom

node_counter = 0
line_counter = 0

#  Find all intersects for current (newest) line segment
def calculate_intersect_coords():
    global intersect_coords, intersect_node_dict
    if len(node_coords) > 1:
        #  x range for test line
        p1 = line_start_coords[-1][0]
        p2 = line_end_coords[-1][0]
        #  Put in correct order
        if p2 > p1:
            p2, p1 = p1, p2
        counter = 0
        for coord_start, coord_end in zip(line_start_coords[:-2], line_end_coords[:-2]):
            p3 = coord_start[0]
            p4 = coord_end[0]
            #  Put in correct order
            if p4 > p3:
                p4, p3 = p3, p4
            #  Calculate x coord of potential intersection
            m1 = line_m[-1]
            b1 = line_b[-1]
            m2 = line_m[counter]
            b2 = line_b[counter]
            counter += 1
            try:
                x = (b2 - b1) / (m1 - m2)
            except:
                x = 0.00000001
            #  Verify coord is an intersection
            if x < p1 and x > p2 and x < p3 and x > p4:
                #  Calculate y coord of intersect
                y = (m1 * x) + b1
                #  Add coordinates (key) and reference index values to
                #  dictionary
                line_num_bot = counter - 1
                line_num_top = len(node_coords) - 2
                intersect_node_dict[(x, y)] = line_num_bot, line_num_top
                intersect_coords.append([x, y])
                #  Update intersections visually
                update_intersections(x, y)


#  Find slope of given line from two points
def find_slope(p1, p2):
    #  (y2 - y1) / (x2 - x1)
    try:
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    except ZeroDivisionError:
        #  Prevent zero division
        slope = 0.000001
    return slope


#  Find y-intercept of given line from two points and slope
def find_y_intercept(p1, slope):
    #  b = y - mx
    return p1[1] - (slope * p1[0])


#  Record line information in arrays
def record_line_info(x, y):
    global node_coords, line_start_coords, line_end_coords, line_m, line_b
    #  Calculate/record coordinate and line information
    node_coords.append([y, x, 0])
    if len(node_coords) > 1:
        #  Change coordinates from [y,x] to [x,y]
        coords_1 = node_coords[-1][0:2]
        x1, y1 = coords_1[1], coords_1[0]
        coords_ordered_1 = [x1, y1]
        line_end_coords.append(coords_ordered_1)

        coords_2 = node_coords[-2][0:2]
        x2, y2 = coords_2[1], coords_2[0]
        coords_ordered_2 = [x2, y2]
        line_start_coords.append(coords_ordered_2)

        line_m_value = find_slope(line_start_coords[-1], line_end_coords[-1])
        line_m.append(line_m_value)
        line_b_value = find_y_intercept(line_start_coords[-1], line_m[-1])
        line_b.append(line_b_value)


#  Perform and store analysis based on drawn knot
def perform_analysis():
    global analysis_results
    #  Don't need to use #add_closure argument for Knot class because it is
    #  purely visual and does not effect the analysis.
    if len(intersect_coords) > 0:
        node_coords_array = np.asarray(node_coords)
        # crossing_num = find_crossing_number()
        #  'Reduced crossing number' is excluded because it is unknown and is
        #  never assigned a value on the online module.
        #  Determinant|Δ(-1)| - Alexander polynomial evaluated at -1
        determinant = pkidsc.knot.Knot(node_coords_array, verbose=False).determinant()
        #  |Δ(exp(2πi/3)| - Alexander polynomial evaluated at 2πi/3
        alexander_1 = pkidsc.knot.Knot(
            node_coords_array, verbose=False
        ).alexander_polynomial(exp((2 * pi * I) / 3))
        #  |Δ(i)| - Alexander polynomial evaluated at i
        alexander_2 = pkidsc.knot.Knot(
            node_coords_array, verbose=False
        ).alexander_polynomial(I)
        #  Vassiliev invariant order 2, v2
        vassiliev_order2 = pkidsc.knot.Knot(
            node_coords_array, verbose=False
        ).vassiliev_degree_2
        #  Vassiliev invariant order 3, v3
        vassiliev_order3 = pkidsc.knot.Knot(
            node_coords_array, verbose=False
        ).vassiliev_degree_3
        #  Store results of analysis
        analysis_results = [
            determinant,
            alexander_1,
            alexander_2,
            vassiliev_order2,
            vassiliev_order3,
        ]


#  Draw new lines and nodes based on mouse click event
def drawline(event):
    global x0, y0, node_counter, line_counter
    intersect = False
    x, y = event.x, event.y
    for coord in intersect_coords:
        #  Create hitbox for over/under intersection switching
        x_low = int(coord[0] - 20)
        x_high = int(coord[0] + 20)
        y_low = int(coord[1] - 20)
        y_high = int(coord[1] + 20)
        if x > x_low and x < x_high and y > y_low and y < y_high:
            intersect = True
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
        record_line_info(x, y)
        calculate_intersect_coords()
    else:
        x_intersect = local_intersect[0]
        y_intersect = local_intersect[1]
        update_intersections(x_intersect, y_intersect)
    all_tags = draw.find_all()
    modify_z_values()


#  Calculate gauss code and update label
def find_gc(event):
    global gc_str
    if len(node_coords) > 1:
        #  Convert to array
        node_coords_array = np.asarray(node_coords)
        #  Calculate gauss code
        closures = clos_var.get()  # Returns opposite of current button state
        if closures == 0:
            gc = pkidsc.spacecurve.SpaceCurve(
                node_coords_array, verbose=False
            ).gauss_code(include_closure=False)
        else:
            gc = pkidsc.spacecurve.SpaceCurve(
                node_coords_array, verbose=False
            ).gauss_code()
        gc_str = str(gc)
        g_code.config(text=gc_str)
        # perform_analysis()

        # results.config(text="Determinant|Δ(-1)|     " + str(analysis_results[0]) + "\n" +
        #                    "|Δ(exp(2πi/3)|     " + str(analysis_results[1]) + "\n" +
        #                    "|Δ(i)|     " + str(analysis_results[2]) + "\n")
        #                    #"Vassiliev order 2, v2     " + str(analysis_results[4]) + "\n" +
        #                    #"Vassiliev order 3, v3     " + str(analysis_results[5]) + "\n")


#  Placehold for button functionality
def button_placeholder():
    print("Hello world")


#  Clear all data and objects on canvas
def clear_canvas(event):
    global x0, y0, node_coords, line_start_coords, line_end_coords, line_m
    global line_b, intersect_coords, intersect_node_dict
    global node_counter, line_counter
    draw.delete("all")
    x0, y0 = 0, 0
    node_coords.clear()
    line_start_coords.clear()
    line_end_coords.clear()
    line_m.clear()
    line_b.clear()
    intersect_coords.clear()
    intersect_node_dict.clear()
    analysis_results.clear()
    g_code.config(text="--")
    results.config(text="--")
    clos_var.set(0)
    node_counter = 0
    line_counter = 0
    intersect_stack_dict.clear()


#  Visually add or remove the closure line segment
def include_closures(event):
    closures = clos_var.get()  # Returns opposite of current button state
    if len(node_coords) >= 3:
        if closures == 0:
            x1, y1 = node_coords[0][1], node_coords[0][0]
            x2, y2 = node_coords[-1][1], node_coords[-1][0]
            draw.create_line(
                x1, y1, x2, y2, fill=linecolor, width=linewidth, tags="closure"
            )
        else:
            draw.delete("closure")


###  Crossing number not calculating properly
###  Find number of total intersections
##def find_crossing_number():
##    #  Find the number of intersections for the closure line
##    num_closure_intersects = 0
##    closures = clos_var.get()
##    if closures == 1:
##        #  Taking second item because node coords in format (y,x,z)
##        x1, x2 = node_coords[0][1], node_coords[-1][1]
##        line_info, p1, p2, p3, p4  = find_possible_intersects(x1,x2)
##        for line in line_info:
##            x = line[0]
##            #  Verify coord is an intersection
##            if x < p1 and x > p2 and x < p3 and x > p4:
##                num_closure_intersects += 1
##    crossing_num = len(intersect_coords) + num_closure_intersects
##    return crossing_num


###  Accepts index number of top/bottom lines and modifies z-values accordingly
##def modify_z_values(top,bot):
##    global node_coords
##    try:
##        node_coords[top][2] = 1
##        node_coords[bot][2] = -1
##    except KeyError:
##        pass

#  Input is the intersection coords
def update_intersections(
    x, y
):  #  function is being passed all the correct intersections, problem with the function itself
    global intersect_stack_dict
    #  Retrieve tag values for intersecting lines
    line_tags = intersect_node_dict.get((x, y))
    tag1_num = line_tags[0]
    tag2_num = line_tags[1]
    #  Generate corresponding tags
    tag1 = "line_" + str(tag1_num)
    tag2 = "line_" + str(tag2_num)
    #  Generate tag for intersect node
    intersect_node_tag = str("node_" + str(x) + "_" + str(y))
    #  If initial intersection, create intersection node
    keys = intersect_stack_dict.keys()
    if intersect_node_tag not in keys:
        draw.create_oval(
            x - 8,
            y - 8,
            x + 8,
            y + 8,
            fill=background_color,
            width=0,
            tags=intersect_node_tag,
        )
        #  Update dictionary values based on user
        if tag1_num > tag2_num:
            #  Key: tag for intersection node, value: tag for first line, tag
            #  for second line, position of first line, position for second
            intersect_stack_dict[intersect_node_tag] = [tag1, tag2, 1, -1]
        else:
            intersect_stack_dict[intersect_node_tag] = [tag1, tag2, -1, 1]
    else:
        intersect_values = intersect_stack_dict.get(intersect_node_tag)
        if intersect_values[2] == 1:
            intersect_stack_dict[intersect_node_tag] = [tag1, tag2, -1, 1]
        else:
            intersect_stack_dict[intersect_node_tag] = [tag1, tag2, 1, -1]

    #  Breakout lines based on position
    keys = intersect_stack_dict.keys()
    above = []
    below = []
    for key in keys:
        key_value = intersect_stack_dict.get(key)
        if key_value[2] == 1:
            above_line = key_value[0]
            below_line = key_value[1]
            above.append(above_line)
            below.append(below_line)
        else:
            above_line = key_value[1]
            below_line = key_value[0]
            above.append(above_line)
            below.append(below_line)
    #  Update positions visually
    for line in below:
        draw.tag_raise(line)
    for node in keys:
        draw.tag_raise(node)
    for line in above:
        draw.tag_raise(line)


#  Obtain tags from intersect coordinates and modify z-values of node
#  coordinate array accordingly
def modify_z_values():
    global node_coords
    for coord in intersect_coords:
        x, y = coord[0], coord[1]
        try:
            intersect_num_list = intersect_node_dict[(x, y)]
            intersect_num = intersect_num_list[0]
            node_coords[-1][2] = 1
            node_coords[intersect_num][2] = -1
        except KeyError:
            continue


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
draw = tk.Canvas(draw_frame, width=800, height=800)

#  Place widget in draw frame
draw.grid(row=0, column=0)

#  Create widgets for right (interface) frame
title = tk.Label(interface_frame, text="WhyKnot", font=("Helvetica", 18))

g_code_var = tk.StringVar()  #  Button var so text can be updated
g_code_var.set("--")
g_code = tk.Label(interface_frame, text="--", font=("Helvetica", 15), wraplength=300)

clos_var = tk.IntVar()
closures = tk.Checkbutton(interface_frame, text="Include closure", variable=clos_var)

file = tk.Button(interface_frame, text="File (f)")
save = tk.Button(interface_frame, text="Save (w)")
# results = tk.Label(interface_frame, text="Results Goes Here")
close = tk.Button(interface_frame, text="Quit (q)")
clear = tk.Button(interface_frame, text="Clear (c)")
coords_realtime = tk.Label(interface_frame, text="--")

#  Place widgets in interface frame
title.grid(row=0, columnspan=2)
g_code.grid(row=3, columnspan=2)
closures.grid(row=2, columnspan=2)
file.grid(row=1, column=0)
save.grid(row=1, column=1)
clear.grid(row=4, column=0)
close.grid(row=4, column=1)
coords_realtime.grid(row=6, columnspan=2)

#  Initialize event handler
draw.bind("<Button-1>", drawline, add="+")
draw.bind("<Button-1>", find_gc, add="+")
clear.bind("<Button-1>", clear_canvas)
root.bind("c", clear_canvas)
close.bind("<Button-1>", lambda e: root.destroy())
root.bind("q", lambda e: root.destroy())
closures.bind("<Button-1>", include_closures)
draw.bind("<Motion>", display_coords_realtime)
root.bind("y", copy_gauss)
# save.bind("<Button-1>", write_data)
# root.bind("w", write_data)

root.mainloop()
