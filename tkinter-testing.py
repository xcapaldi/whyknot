import tkinter as tk
import numpy as np

### GENERAL FUNCTIONS ###

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

### DRAWING ###

# initialize lists to hold tags canvas elements
nodetags=[] # x, y
bridgetags=[] # xbounds, ybounds, (z?)
linetags=[] # xbounds, ybounds, (slope?)

# graphical variables
canvasbackground = "#d9d9d9"
noderadius = 5
nodecolor = "#ce0000"
linethickness = 2
linecolor = "#5a79a5"
activeline = "#ffcc00"

# function to extract information from tags
def extracttaginfo(tag):
    splittag = tag.split("_")
    if splittag[0]==("node"):
        # return [x, y]
        return splittag[1:3]
    elif splittag[0]==("line"):
        # return [x0, y0, x, y]
        return splittag[1:5]
    # otherwise it is a bridge
    else:
        # return [x0, y0, x, y, z]
        return splittag[1:6]

# function to draw line nodes
def drawnode(x, y, radius, color):
    tag = "node_" + str(x) + "_" + str(y)
    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, width=0,
    tags=tag)
    nodetags.append(tag)

def drawline(x0, y0, x, y, thickness, color):
    tag = "line_" + str(x0) + "_" + str(x) + "_" + str(y0) + "_" + str(y)
    canvas.create_line(x0, y0, x, y, fill = color, width = thickness, tags=tag)

# main drawing function
def drawsegment(x,y):
    drawnode(x,y,noderadius,nodecolor)
    # check if there is an initial node
    if len(nodetags)!=1:
        # use use the coordinates of the previous node
        previousnode = extracttaginfo(nodetags[-2])
        drawline(float(previousnode[0]),float(previousnode[1]),x,y,linethickness,linecolor)
        # raise the nodes to the top of the canvas so they are drawn over the lines
        canvas.tag_raise(nodetags[-1])
        canvas.tag_raise(nodetags[-2])

def canvasinteract(event):
    # capture mouse location
    x, y = event.x, event.y
    # this is the size of the bounding box for determining intersections
    hbsize = 20
    points = canvas.find_enclosed(x-hbsize/2,y+hbsize/2,x+hbsize/2,y-hbsize/2)
    tags = canvas.gettags(points)
    # check if anything was enclosed
    if len(tags) > 0:
        for tag in tags:
            if tag.startswith("bridge"):
                # bridge switch function here
                # what happens if we have two close bridges?!
                print("SWITCH BRIDGE")
        
    # otherwise just draw a new line segment
    else:
        drawsegment(x,y)

# TODO TODO TODO


#    drawsegment(x,y)
    
# CAN USE activefill to show when switching
# can also use canvas.config(cursor="exchange")

### TKINTER ###

# create main window
root = tk.Tk()
root.title("WhyKnot")
root.geometry("1280x720")

# create main frames within the root frame
drawframe = tk.Frame(root, width=980, height=720)
interfaceframe = tk.Frame(root, width=300, height=720)

# set geometry manager class for main frames and organize within root frame
drawframe.grid(column=0, row=0, sticky = "nsw")
interfaceframe.grid(column=1, row=0, sticky = "nse")

# create canvas widget for draw frame
canvas = tk.Canvas(drawframe, bg=canvasbackground, cursor="cross", width=980, height=720)

# place widget in draw frame
canvas.grid(row=0, column=0)

# create widgets for interface frame
title = tk.Label(interfaceframe, text="WhyKnot", font=("Helvetica", 18))

# place widgets in interface frame
title.grid(row=0, columnspan=2)

# event handlers
canvas.bind("<Button-1>", drawsegment, add="+")

# begin progam main loop
root.mainloop()
