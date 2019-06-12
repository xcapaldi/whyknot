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
bridgewidth = 3
background_color = "#d9d9d9"

#  Create lists to store variables
knot_coords = []  #  Includes node coords and bridges
node_coords = []  #  Includes node coords only
line_start_coords = []
line_end_coords = []
line_m = []
line_b = []
intersect_coords = []
closure_line_info = []
closure_intersects = []

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
intersected_list = []  #  Line number stored if intersected

#  Bounds for slope (to identify when to rotate line 90 degrees)
m_lower_bound = -5
m_upper_bound = 5


#  Find all intersects for current (newest) line segment
#  Input is x-range, slope and y-intercept for test line
def calculate_intersect_coords(p1, p2, m1, b1, closure=False):
    global intersect_coords, intersect_node_dict
    intercepts = []
    #  Put in correct order
    if p2 > p1:
        p2, p1 = p1, p2
    counter = 0
    
    if closure:
        coord_index = -1
    else:
        coord_index = -2
        
    for coord_start, coord_end in zip(line_start_coords[:coord_index], line_end_coords[:coord_index]):
        p3 = coord_start[0]
        p4 = coord_end[0]
        #  Put in correct order
        if p4 > p3:
            p4, p3 = p3, p4
        #  Calculate x coord of potential intersection
        m2 = line_m[counter]
        b2 = line_b[counter]
        counter += 1
        try:
            x = (b2 - b1) / (m1 - m2)
        except:
            print("exception")
            x = 0.0000001
        #  Verify coord is an intersection
        if x < p1 and x > p2 and x < p3 and x > p4:
            #  Calculate y coord of intersect
            y = (m1 * x) + b1
            line_num_bot = counter - 1
            line_num_top = len(node_coords) - 2
            intercepts.append([x,y, line_num_bot, line_num_top])
    return intercepts

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
    global node_coords, knot_coords, line_start_coords, line_end_coords, line_m, line_b
    #  Calculate/record coordinate and line information
    node_coords.append([x, y, 0])
    knot_coords.append([x, y, 0])
    if len(node_coords) > 1:
        line_end_coords.append([node_coords[-1][0], node_coords[-1][1]])
        line_start_coords.append([node_coords[-2][0], node_coords[-2][1]])
        
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
        knot_coords_array = np.asarray(knot_coords)
        # crossing_num = find_crossing_number()
        #  'Reduced crossing number' is excluded because it is unknown and is
        #  never assigned a value on the online module.
        #  Determinant|Δ(-1)| - Alexander polynomial evaluated at -1
        determinant = pkidsc.knot.Knot(knot_coords_array, verbose=False).determinant()
        #  |Δ(exp(2πi/3)| - Alexander polynomial evaluated at 2πi/3
        alexander_1 = pkidsc.knot.Knot(
            knot_coords_array, verbose=False
        ).alexander_polynomial(exp((2 * pi * I) / 3))
        #  |Δ(i)| - Alexander polynomial evaluated at i
        alexander_2 = pkidsc.knot.Knot(
            knot_coords_array, verbose=False
        ).alexander_polynomial(I)
        #  Vassiliev invariant order 2, v2
        vassiliev_order2 = pkidsc.knot.Knot(
            knot_coords_array, verbose=False
        ).vassiliev_degree_2
        #  Vassiliev invariant order 3, v3
        vassiliev_order3 = pkidsc.knot.Knot(
            knot_coords_array, verbose=False
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

#  Calculate gauss code and update label
def find_gc(event):
    global gc_str
    if len(knot_coords) > 1:
        #  Convert to array
        knot_coords_array = np.asarray(knot_coords)
        gc = pkidsc.spacecurve.SpaceCurve(
            knot_coords_array, verbose=False).gauss_code(include_closure=False)
        gc_str = str(gc)
        g_code.config(text=gc_str)

#  Placehold for button functionality
def button_placeholder():
    print("Hello world")


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


#  Visually add or remove the closure line segment
def include_closures(event):
    global closure_line_info, closure_intersects

    #  Record previous state of node_coords and knot_coords
    node_coords_backup = []
    knot_coords_backup = []
    for coord in node_coords:
        node_coords_backup.append(coord)
    for coord in knot_coords:
        knot_coords_backup.append(coord)
    #print("backup" + str(node_coords_backup))
    #  Delete any previous closure lines and return them to their previous state...
    closure_return_state()
    
    closure = clos_var.get()  # Returns opposite of current button state
    
    if len(node_coords) > 1:
        if closure == 0:
            #  Calculate info about closure line
            x1 = node_coords[0][1]
            y1 = node_coords[0][0]
            x2 = node_coords[-1][1]
            y2 = node_coords[-1][0]
            closure_m = find_slope([x1, y1], [x2, y2])
            closure_b = find_y_intercept([x1, y1], closure_m)
            closure_line_info = [[x1, y1], [x2, y2], closure_m, closure_b]

            #  Find intersects for closure line
            closure_intersects = calculate_intersect_coords(x1, x2, closure_m,
                                                            closure_b, closure=True)

            #  Verify start or end coord not included in list
            start_x, start_y = round(x1), round(y1)
            end_x, end_y = round(x2), round(y2)
            count = 0
            for intersect in closure_intersects:
                intersect_x = round(intersect[0])
                intersect_y = round(intersect[1])
                if intersect_x == start_x and intersect_y == start_y:
                    del closure_intersects[count]
                if intersect_x == end_x and intersect_y == end_y:
                    del closure_intersects[count]
                count +=1
                
            #  Create new closure line and change values as necessary...
            if len(closure_intersects) == 0:
                draw.create_line(x1, y1, x2, y2, fill=linecolor,
                                 width=linewidth, tags="closure")
            else:
                #  Add closure line to node coords
                node_coords.append([x2, y2, 1])
                for i in closure_intersects:
                    #  i = [x,y, line_num_bot, line_num_top]
                    line_num_bot = i[2]
                    #  Record intersect in dictionary
                    intersect_node_dict[(i[0], i[1])] = i[2], "c"
                    #  Create actual intersect line segments
                    create_intersections(i[0], i[1])

#  Returns line segments and z-values to state prior to closure line
def closure_return_state():
    draw.delete("closure")
    draw.delete("closure_crossroad")                 


#  Calculate the 4 coord positions for an intersection bridge
def calculate_bridge_coords(line_start, line_end, x, y, m, b):
    bridge_coords = []
    #  Variable to track if bridge coords need to be swapped
    swap = False
    #  Bridge width (multiply by two for total width)
    bridge_width = 5
    if m < m_lower_bound or m > m_upper_bound:
        if m > 0:
            y_upper = y + bridge_width
            y_lower = y - bridge_width
        else:
            y_upper = y - bridge_width
            y_lower = y + bridge_width
        x_upper = (y_upper - b) / m
        x_lower = (y_lower - b) / m
        
        #  Determine if coords need to be swapped
        if line_start[1] > line_end[1]:  #  Line visually oriented end to start
            if (line_start[1] - y_upper) > (line_start[1] - y_lower):
                swap = True
        else:                            #  Line visually oriented start to end
            if (line_start[1] + y_upper) > (line_start[1] + y_lower):
                swap = True 
    else:
        x_upper = x - bridge_width
        y_upper = (m*x_upper)+b
        x_lower = x + bridge_width
        y_lower = (m*x_lower)+b

    #  Swap coords as necessary
    if swap:
        bridge_start = [x_lower, y_lower]
        bridge_end = [x_upper, y_upper]
    else:
        bridge_start = [x_upper, y_upper]
        bridge_end = [x_lower, y_lower]

    #  Generate coord positions for bridge
    c1 = [bridge_start[0], bridge_start[1], 0]
    c2 = [bridge_start[0], bridge_start[1], 1]
    c3 = [bridge_end[0], bridge_end[1], 1]
    c4 = [bridge_end[0], bridge_end[1], 0]

    return [c1, c2, c3, c4]


#  Visually represent line intersections and update z-values for
#  initial crossings.
def create_intersections(x, y):
    global line1_tag, line2_tag, intersect_crossroads, closure_line_info, knot_coords
    closure = False
    
    #  Retrieve tag values for intersecting lines
    line_tags = intersect_node_dict.get((x, y))
    
    #  Check if line is the closure line
    if line_tags[1] == "c":
        closure = True
        tag1_num = line_tags[0]
        #  Generate tags
        tag1 = "line_" + str(tag1_num)
        tag2 = "closure"
    else:
        tag1_num = line_tags[0]  # bottom line/ line being intersected
        tag2_num = line_tags[1]  # top line / line intersecting
        #  Generate corresponding tags
        tag1 = "line_" + str(tag1_num)
        tag2 = "line_" + str(tag2_num)
        
    #  Find all other intersections on same line
    line1_coords = []
    line2_coords = []
    if closure:
        #  Record previously calculated intersects for closure line
        for intersect in closure_intersects:
            line2_coords.append([intersect[0], intersect[1]])
        for intersect in intersect_coords:
            intersect_line_nums = intersect_node_dict.get((intersect[0], intersect[1]))
            line1_num = intersect_line_nums[0]
            line2_num = intersect_line_nums[1]
            if line1_num == tag1_num or line2_num == tag1_num:
                line1_coords.append(intersect)
        line1_coords.append([x,y])
    else:
        for intersect in intersect_coords:
            intersect_line_nums = intersect_node_dict.get((intersect[0], intersect[1]))
            line1_num = intersect_line_nums[0]
            line2_num = intersect_line_nums[1]
            if line1_num == tag1_num or line2_num == tag1_num:
                line1_coords.append(intersect)
            if line1_num == tag2_num or line2_num == tag2_num:
                line2_coords.append(intersect)

    #  Retrieve start and end coords for the two intersecting lines and add to
    #  intersection lists
    if closure:
        line1_startpoint = line_start_coords[tag1_num]
        line1_endpoint = line_end_coords[tag1_num]
        line2_startpoint = closure_line_info[0]
        line2_endpoint = closure_line_info[1]
    else:
        line1_startpoint = line_start_coords[tag1_num]
        line1_endpoint = line_end_coords[tag1_num]
        line2_startpoint = line_start_coords[tag2_num]
        line2_endpoint = line_end_coords[tag2_num]
        
    line1_coords.append(line1_startpoint)
    line1_coords.append(line1_endpoint)
    line2_coords.append(line2_startpoint)
    line2_coords.append(line2_endpoint)
    
    #  Sort intersection lists
    line1_coords.sort()
    line2_coords.sort()

    #  Delete all previous line segments
    if closure:
        draw.delete(tag1)
        #closure_return_state()
        if tag1 in tag_dict:
            segment_tags1 = tag_dict.get(tag1)
            draw.delete(segment_tags1)
    else:
        draw.delete(tag1)
        draw.delete(tag2)
        if tag1 in tag_dict:
            segment_tags1 = tag_dict.get(tag1)
            draw.delete(segment_tags1)
        if tag2 in tag_dict:
            segment_tags2 = tag_dict.get(tag2)
            draw.delete(segment_tags2)

    #  Generate tags for new line segments and add to dictionary
    if closure:
        line1_tag = str("line1_" + str(x) + "_" + str(y))
        line2_tag = "closure_segments"
    else:
        line1_tag = str("line1_" + str(x) + "_" + str(y))
        line2_tag = str("line2_" + str(x) + "_" + str(y))
    tag_dict[tag1] = line1_tag
    tag_dict[tag2] = line2_tag
    
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
    if closure:
        line2_m = closure_line_info[2]
        line2_b = closure_line_info[3]
    else:
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
    if closure:
        crossroad_tag = str("closure_crossroad_" + str(x) + "_" + str(y))
    else:
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

    #  Add initial bridge values to knot_coords

    #  Identify all intersects along the given line and order them
    bridge_intersects = line2_coords[1:-1]
    bridge_intersects.sort()
        
    #  Identify exact index value at which to insert ordered bridge coords
    bridge_index = (line2_num + (len(intersected_list)*4) +1)
    #print(bridge_index)

    #  Store locations and order of intersects to use for later indexing
    if line2_num not in intersected_list:
        intersected_list.append(line2_num)

    #  Calculate ordered bridge coords
    bridge_coords = []
    for coord in bridge_intersects:
        bridge_coord_list = calculate_bridge_coords(line_start_coords[line2_num],
                                         line_end_coords[line2_num], coord[0],
                                         coord[1], line2_m, line2_b)
        bridge_coords.append(bridge_coord_list)

    #  Insert bridge coords into knot_coords
    for bridge in bridge_coords:
        for coord in bridge[::-1]:
            knot_coords.insert(bridge_index, coord)
            bridge_index +=1
    print('\n')
    print(knot_coords)


#  Update currently existing crossroads and modify bridge coords
def update_crossroads(x,y, closure = False):
    #  Generate tag
    if closure:
        crossroad_tag = str("closure_crossroad_" + str(x) + "_" + str(y))
    else:
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
    tag1_num = line_tags[1]  # bottom line/ line being intersected   #  WAS line_tags[0]
    if closure:
        if node_coords[-1][2] == -1:
            node_coords[-1][2] = 1
        else:
            node_coords[-1][2] = -1
            
##        if node_coords[tag1_num][2] == -1:
##            #node_coords[tag1_num][2] = 1
##            node_coords[-1][2] = -1
##        else:
##            node_coords[tag1_num][2] = -1
##            node_coords[-1][2] = 1
    else:
        tag2_num = line_tags[0]  # top line / line intersecting   #  WAS line_tags[1]
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
#closures.bind("<Button-1>", find_gc)
draw.bind("<Motion>", display_coords_realtime)
root.bind("y", copy_gauss)
# save.bind("<Button-1>", write_data)
# root.bind("w", write_data)

root.mainloop()
