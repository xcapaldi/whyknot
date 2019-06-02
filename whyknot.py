#  WhyKnot
#  Graphical wrapper for PyKnotID package
#  Xavier and Luc Capaldi


import tkinter as tk
import tkinter.filedialog as fd
import numpy as np
import pyknotid
import pyknotid.spacecurves as pkidsc
#from pyknotid.representations import GaussCode, Representation
from sympy import Symbol, exp, I, pi
import csv

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
#  Placeholder tag values
line1_tag = "tag1_0_0"
line2_tag = "tag2_0_0"
tag_dict = {}  #  Stores tag for line segments
intersect_crossroads = {}  #  Positions for crossroad lines
crossroad_start_end = {}   #  Current start/end coordinates for crossroads

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
                create_intersections(x, y)


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
        update_crossroads(x_intersect, y_intersect)

#  Calculate gauss code, alexander polynomial, determinant, 2nd and 3rd degree vassiliev
#  invariants and updates the label
def find_gc(event):
    global gc_str
    global alexander_str
    global determinant_str
    global vassiliev2_str
    global vassiliev3_str
    if len(node_coords) > 1:
        #  Convert to array
        node_coords_array = np.asarray(node_coords)
        ##np.append(node_coords_array,node_coords[0])
        # Calculate gauss code
        #closures = clos_var.get()  # Returns opposite of current button state
        #if closures == 0:
        #    gc = pkidsc.spacecurve.SpaceCurve(
        #        node_coords_array, verbose=False
        #    ).gauss_code(include_closure=False)
        #else:
        #    gc = pkidsc.spacecurve.SpaceCurve(
        #        node_coords_array, verbose=False
        #    ).gauss_code()
        k = pkidsc.Knot(node_coords_array)
        gc = k.gauss_code()
        ##gc.simplify()
        #ap = 
        #det = k.determinant()
        #vas2 = 
        #vas3 = 
        g_code.config(text=str(gc))
        # perform_analysis()

        # results.config(text="Determinant|Δ(-1)|     " + str(analysis_results[0]) + "\n" +
        #                    "|Δ(exp(2πi/3)|     " + str(analysis_results[1]) + "\n" +
        #                    "|Δ(i)|     " + str(analysis_results[2]) + "\n")
        #                    #"Vassiliev order 2, v2     " + str(analysis_results[4]) + "\n" +
        #                    #"Vassiliev order 3, v3     " + str(analysis_results[5]) +
        #                    "\n")

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
    clos_var.set(0)
    node_counter = 0
    line_counter = 0
    intersect_stack_dict.clear()
    tag_dict.clear()
    intersect_crossroads.clear()
    crossroad_start_end.clear()


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

#  Visually represent line intersections and update z-values for
#  initial crossings.
def create_intersections(x, y):
    global line1_tag, line2_tag, intersect_crossroads
    
    #  Retrieve tag values for intersecting lines
    line_tags = intersect_node_dict.get((x, y))
    tag1_num = line_tags[0]  # bottom line/ line being intersected
    tag2_num = line_tags[1]  # top line / line intersecting

    #  Change z-values for initial intersection
    node_coords[tag1_num][2] = -1
    node_coords[tag2_num][2] = 1
    
    #  Generate corresponding tags
    tag1 = "line_" + str(tag1_num)
    tag2 = "line_" + str(tag2_num)

    #  Find all other intersections on same line
    line1_coords = []
    line2_coords = []
    for intersect in intersect_coords:
        intersect_x = intersect[0]
        intersect_y = intersect[1]
        intersect_line_nums = intersect_node_dict.get((intersect_x, intersect_y))
        line1_num = intersect_line_nums[0]
        line2_num = intersect_line_nums[1]
        if line1_num == tag1_num or line2_num == tag1_num:
            line1_coords.append(intersect)
        if line1_num == tag2_num or line2_num == tag2_num:
            line2_coords.append(intersect)
            
    #  Retrieve start and end coords for the two intersecting lines
    line1_startpoint = line_start_coords[tag1_num]
    line1_endpoint = line_end_coords[tag1_num]
    line2_startpoint = line_start_coords[tag2_num]
    line2_endpoint = line_end_coords[tag2_num]
    
    #  Add start/end coords to intersection lists
    line1_coords.append(line1_startpoint)
    line1_coords.append(line1_endpoint)
    line2_coords.append(line2_startpoint)
    line2_coords.append(line2_endpoint)
    
    #  Sort intersection lists
    line1_coords.sort()
    line2_coords.sort()
    
    #  Delete all previous line segments
    draw.delete(tag1)
    draw.delete(tag2)
    if tag1 in tag_dict:
        segment_tags1 = tag_dict.get(tag1)
        draw.delete(segment_tags1)
    if tag2 in tag_dict:
        segment_tags2 = tag_dict.get(tag2)
        draw.delete(segment_tags2)

    #  Generate tags for new line segments and add to dictionary
    line1_tag = str("line1_" + str(x) + "_" + str(y))
    line2_tag = str("line2_" + str(x) + "_" + str(y))
    tag_dict[tag1] = line1_tag
    tag_dict[tag2] = line2_tag

    #  Bounds for slope (to identify when to rotate line 90 degrees)
    m_lower_bound = -5
    m_upper_bound = 5
    
    #  Find all start and endpoints for line segments along line1
    line1_segment_coords = []
    position1 = 0
    line1_m = line_m[tag1_num]
    line1_b = line_b[tag1_num]
    for intersect1, intersect2 in zip(line1_coords[0:], line1_coords[1:]):
        #  Initial line segment
        if position1 == 0:
            line1_segment_coords.append([intersect1[0], intersect1[1]])
            if line1_m < m_lower_bound or line1_m > m_upper_bound:
                if line1_m > 0:
                    y_lower = intersect2[1]-6
                else:
                    y_lower = intersect2[1]+6
                x_lower = (y_lower - line1_b) / line1_m
            else:
                x_lower = intersect2[0]-6
                y_lower = (line1_m*x_lower)+line1_b
            line1_segment_coords.append([x_lower, y_lower])

        #  Final line segment     
        elif position1 == len(line1_coords)-2:
            if line1_m < m_lower_bound or line1_m > m_upper_bound:
                if line1_m > 0:
                    y_upper = intersect1[1]+6
                else:
                    y_upper = intersect1[1]-6
                x_upper = (y_upper - line1_b) / line1_m
            else:
                x_upper = intersect1[0]+6
                y_upper = (line1_m*x_upper)+line1_b
            line1_segment_coords.append([x_upper, y_upper])
            line1_segment_coords.append(intersect2)
            
        #  All intermediary line segments
        else:
            if line1_m < m_lower_bound or line1_m > m_upper_bound:
                if line1_m > 0:
                    y_upper = intersect1[1]+6
                    y_lower = intersect2[1]-6
                else:
                    y_upper = intersect1[1]-6
                    y_lower = intersect2[1]+6
                x_upper = (y_upper - line1_b) / line1_m
                x_lower = (y_lower - line1_b) / line1_m
            else:
                x_upper = intersect1[0]+6
                y_upper = (line1_m*x_upper)+line1_b
                x_lower = intersect2[0]-6
                y_lower = (line1_m*x_lower)+line1_b
            line1_segment_coords.append([x_upper, y_upper])
            line1_segment_coords.append([x_lower, y_lower])
        position1 +=1
        
    #  Find all start and endpoints for line segments along line2
    line2_segment_coords = []
    position2 = 0
    line2_m = line_m[tag2_num]
    line2_b = line_b[tag2_num]
    for intersect1, intersect2 in zip(line2_coords[0:], line2_coords[1:]):
        #  Initial line segment
        if position2 == 0:
            line2_segment_coords.append([intersect1[0], intersect1[1]])
            if line2_m < m_lower_bound or line2_m > m_upper_bound:
                if line2_m > 0:
                    y_lower = intersect2[1]-6
                else:
                    y_lower = intersect2[1]+6
                x_lower = (y_lower - line2_b) / line2_m
            else:
                x_lower = intersect2[0]-6
                y_lower = (line2_m*x_lower)+line2_b
            line2_segment_coords.append([x_lower, y_lower])
            
        #  Final line segment
        elif position2 == len(line2_coords)-2:
            if line2_m < m_lower_bound or line2_m > m_upper_bound:
                if line2_m > 0:
                    y_upper = intersect1[1]+6
                else:
                    y_upper = intersect1[1]-6
                x_upper = (y_upper - line2_b) / line2_m
            else:
                x_upper = intersect1[0]+6
                y_upper = (line2_m*x_upper)+line2_b
            segment_coords = [x_upper, y_upper]
            line2_segment_coords.append([x_upper, y_upper])
            line2_segment_coords.append([intersect2[0], intersect2[1]])

        #  All intermediary line segments 
        else:
            if line2_m < m_lower_bound or line2_m > m_upper_bound:
                if line2_m > 0:
                    y_upper = intersect1[1]+6
                    y_lower = intersect2[1]-6
                else:
                    y_upper = intersect1[1]-6
                    y_lower = intersect2[1]+6
                x_upper = (y_upper - line2_b) / line2_m
                x_lower = (y_lower - line2_b) / line2_m
            else:
                x_upper = intersect1[0]+6
                y_upper = (line2_m*x_upper)+line2_b
                x_lower = intersect2[0]-6
                y_lower = (line2_m*x_lower)+line2_b
            line2_segment_coords.append([x_upper, y_upper])
            line2_segment_coords.append([x_lower, y_lower])
        position2 +=1
   
    #  Create all new line segments
    for start, end in zip(line1_segment_coords[0::2], line1_segment_coords[1::2]):
        draw.create_line(start[0], start[1], end[0], end[1],
                         fill=linecolor, width=linewidth, tags = line1_tag)
    for start, end in zip(line2_segment_coords[0::2], line2_segment_coords[1::2]):
        draw.create_line(start[0], start[1], end[0], end[1],
                         fill=linecolor, width=linewidth, tags = line2_tag)

    #  Generate tag for intersect crossroads
    crossroad_tag = str("crossroad_" + str(x) + "_" + str(y))
    
    #  Find crossroad coords
    #  Line 1
    if line1_m < m_lower_bound or line1_m > m_upper_bound:
        if line1_m > 0:
            crossroad1_y_upper = y+6
            crossroad1_y_lower = y-6
        else:
            crossroad1_y_upper = y-6
            crossroad1_y_lower = y+6
        crossroad1_x_upper = (crossroad1_y_upper - line1_b) / line1_m
        crossroad1_x_lower = (crossroad1_y_lower - line1_b) / line1_m   
    else:
        crossroad1_x_upper = x+6
        crossroad1_x_lower = x-6
        crossroad1_y_upper = (line1_m*crossroad1_x_upper)+line1_b
        crossroad1_y_lower = (line1_m*crossroad1_x_lower)+line1_b
    #  Line 2
    if line2_m < m_lower_bound or line2_m > m_upper_bound:
        if line2_m > 0:
            crossroad2_y_upper = y+6
            crossroad2_y_lower = y-6
        else:
            crossroad2_y_upper = y-6
            crossroad2_y_lower = y+6 
        crossroad2_x_upper = (crossroad2_y_upper - line2_b) / line2_m
        crossroad2_x_lower = (crossroad2_y_lower - line2_b) / line2_m
    else:
        crossroad2_x_upper = x+6
        crossroad2_x_lower = x-6
        crossroad2_y_upper = (line2_m*crossroad2_x_upper)+line2_b
        crossroad2_y_lower = (line2_m*crossroad2_x_lower)+line2_b 
        
    #  Add crossroad coords to dictionary, lower line then upper line
    intersect_crossroads[crossroad_tag] = [[crossroad1_x_upper,crossroad1_y_upper,
                                            crossroad1_x_lower,crossroad1_y_lower],
                                           
                                           [crossroad2_x_upper,crossroad2_y_upper,
                                            crossroad2_x_lower,crossroad2_y_lower]]

    #  Draw initial crossroad line
    draw.create_line(crossroad2_x_upper, crossroad2_y_upper,
                     crossroad2_x_lower, crossroad2_y_lower,
                         fill=linecolor, width=linewidth, tags = crossroad_tag)

    #  Record current start/end coordinates for crossroad line
    crossroad_start_end[crossroad_tag] = [crossroad2_x_upper,
                                          crossroad2_y_upper,
                                          crossroad2_x_lower,
                                          crossroad2_y_lower]

#  Update currently existing crossroads and modify z-value
def update_crossroads(x,y):
    #  Generate tag
    crossroad_tag = str("crossroad_" + str(x) + "_" + str(y))
    
    #  Delete current crossroad line
    draw.delete(crossroad_tag)
    
    #  Retrieve the current start/end coordinates
    current_coords = crossroad_start_end.get(crossroad_tag)
    current_x_upper = current_coords[0]
    current_y_upper = current_coords[1]
    current_x_lower = current_coords[2]
    current_y_lower = current_coords[3]
    
    #  Retrieve both possible line positions
    possible_positions = intersect_crossroads.get(crossroad_tag)
    
    #  Change line to opposite of current position and update start/end dict
    if (current_x_upper == possible_positions[0][0] and
        current_y_upper == possible_positions[0][1] and
        current_x_lower == possible_positions[0][2] and
        current_y_lower == possible_positions[0][3]):
        draw.create_line(possible_positions[1][0], possible_positions[1][1],
                         possible_positions[1][2], possible_positions[1][3],
                         fill=linecolor, width=linewidth, tags = crossroad_tag)
        crossroad_start_end[crossroad_tag] = (possible_positions[1][0],
                                              possible_positions[1][1],
                                              possible_positions[1][2],
                                              possible_positions[1][3])
    else:
        draw.create_line(possible_positions[0][0], possible_positions[0][1],
                         possible_positions[0][2], possible_positions[0][3],
                         fill=linecolor, width=linewidth, tags = crossroad_tag)
        crossroad_start_end[crossroad_tag] = (possible_positions[0][0],
                                              possible_positions[0][1],
                                              possible_positions[0][2],
                                              possible_positions[0][3])
    
    #  Modify z-value, change to opposite
    line_tags = intersect_node_dict.get((x, y))
    tag1_num = line_tags[0]  # bottom line/ line being intersected
    tag2_num = line_tags[1]  # top line / line intersecting
    if node_coords[tag1_num][2] == -1 and node_coords[tag2_num][2] == 1:
        node_coords[tag1_num][2] = 1
        node_coords[tag2_num][2] = -1
    else:
        node_coords[tag1_num][2] = -1
        node_coords[tag2_num][2] = 1


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
    # set number of entries to -1 initially so we don't count the header
    numknots = -1
    root.filename = fd.askopenfilename(initialdir = "/", title = "Select file",filetypes=[("comma-separated values",".csv")])
    filename.config(text=root.filename.split("/")[-1])
    # update numknots NEEDS TESTING
    with  open(root.filename, newline='') as csvfile:
        knotentries = csv.reader(csvfile, delimiter = ' ', quotechar="|")
        for row in knotentries:
            numknots+=1
    entries.config(text=str(numknots)+" entries")

# new file to save data to
def new_file(event):
    global numknots
    # ask for new filename and location
    root.filename = fd.asksaveasfilename(initialdir = "/", title = "New file",
    defaultextension=".csv")
    # make file
    with open(root.filename,'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["gauss","crossingnum","alexander"])
    # update filename
    filename.config(text=root.filename.split("/")[-1])
    # set number of knots to 0
    numknots = 0

def write_data(event):
    global numknots
    numknots=numknots+1
    entries.config(text=str(numknots)+" entries")

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
save.grid(row=2, columnspan=2)
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
draw.bind("<Motion>", display_coords_realtime)
root.bind("y", copy_gauss)
save.bind("<Button-1>", write_data)
root.bind("w", write_data)
file.bind("<Button-1>",open_file)
new.bind("<Button-1>",new_file)

root.mainloop()
