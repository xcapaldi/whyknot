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
    return [xbound, ybound, slope]

# find the y-intercept of a given line
def findyintercept(x,y,m):
    b = y - (m * x)
    return b

# check if intersect between two lines falls within their range
def checkrange(xbound1,xbound2,ybound1,ybound2,intersect):
    line1x, line2x, line1y, line2y = [False]*4
    # check xrange of first line
    if intersect[0] > min(xbound1) and intersect[0] < max(xbound1):
        line1x = True
    # check x range of second line
    if  intersect[0] > min(xbound2) and intersect[0] < max(xbound2):
        line2x = True
    # check y range of first line
    if intersect[1] > min(ybound1) and intersect[1] < max(ybound1):
        line1y = True
    # check y range of second line
    if intersect[1] > min(ybound2) and intersect[1] < max(ybound2):
        line2y = True
    if line1x and line2x and line1y and line2y == True:
        return True
    else:
        return False

# check if two lines intersect
def checkintersect(xbound1,xbound2,ybound1,ybound2,slope1,slope2):
    #check if line 1 is vertical
    if slope1 == None:
        # in this case, the two lines intersect everwhere
        if slope2 == None:
            # not correct but sufficient for the purposes of this script
            return None
        # otherwise, only line 1 is vertical
        else:
            b2=findyintercept(xbound2[0],ybound2[0],slope2)
            xintersect= xbound1[0]
            yintersect= slope2 * xintersect + b2
            # check if intersect in range
            if checkrange(xbound1,xbound2,ybound1,ybound2,[xintersect,yintersect]) == True:
                return [xintersect, yintersect]
            else:
                return None
    # check if line 2 is vertical
    elif slope2 == None:
        # previous conditial checked if line 1 was vertical
        b1=findyintercept(xbound1[0],ybound1[0],slope1)
        xintersect= xbound2[0]
        yintersect= slope1 * xintersect + b1
        # check if intersect in range
        if checkrange(xbound1,xbound2,ybound1,ybound2,[xintersect,yintersect]) == True:
            return [xintersect, yintersect]
        else:
            return None
    # if neither line is vertical
    else:
        b1=findyintercept(xbound1[0],ybound1[0],slope1)
        b2=findyintercept(xbound2[0],ybound2[0],slope2)
        xintersect= (b2-b1)/(slope1-slope2)
        yintersect= slope1 * xintersect + b1
        # check if intersect in range
        if checkrange(xbound1,xbound2,ybound1,ybound2,[xintersect,yintersect]) == True:
            return [xintersect, yintersect]
        else:
            return None

# check if two lines intersect
#def checkintersect(xbound1,xbound2,ybound1,ybound2,slope1,slope2):
#    # check if we have overlap in x range first
#    if max(xbound1) > min(xbound2) and min(xbound1) < max(xbound2):
#        # then check if we have overlap in y range
#        if max(ybound1) > min(ybound2) and min(ybound1) < max(ybound2):
#            # then check if line 1 is vertical
#            if slope1 == None:
#                # in this case, the two lines intersect everywhere
#                if slope2 == None:
#                    # technically not correct but for the purposes of this script it will
#                    # suffice
#                    return None 
#                # otherwise, only line 1 is vertical
#                else:
#                    b2=findyintercept(xbound2[0],ybound2[0],slope2)
#                    xintersect = xbound1[0]
#                    yintersect = slope2 * xintersect + b2
#                    return [xintersect, yintersect]
#            elif slope2 == None:
#                # the previous conditional already checked if line 1 was vertical
#                b1=findyintercept(xbound1[0],ybound1[0],slope1)
#                xintersect = xbound2[0]
#                yintersect = slope1 * xintersect + b1
#                return [xintersect, yintersect]
#            # if neither line is vertical
#            else:
#                b1=findyintercept(xbound1[0],ybound1[0],slope1)
#                b2=findyintercept(xbound2[0],ybound2[0],slope2)
#                xintersect = (b2-b1)/(slope1-slope2)
#                yintersect = slope1 * xintersect + b1
#                return [xintersect, yintersect]
#        else:
#            return None # outside y range
#    else:
#        return None # outside x range

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
def definebridge(xintersect,yintersect,slope,radius,bridgeheight):
    # slope represents the top line
    # if top line is vertical
    if slope == None:
        x = 0
        y = radius
    # else if top line has an angle from vertical
    else:
        # find angle from slope
        angle = np.arctan(slope)
        x = radius*np.cos(angle)
        y = radius*np.sin(angle)
    bridge=[[xintersect-x,xintersect+x],[yintersect-y,yintersect+y],bridgeheight]
    return bridge

### DRAWING ###

# initialize lists to hold tags canvas elements
nodetags=[] # x, y
bridgetags=[] # xbounds, ybounds, (z?)
linetags=[] # xbounds, ybounds, (slope?)
closuretag = None # xbounds, ybounds

# graphical variables
canvasbackground = "#d9d9d9"
noderadius = 5
nodecolor = "#ce0000"
linethickness = 2
linecolor = "#5a79a5"
closurecolor = "#96439d"
activenode= "#000000"
bridgeheight=1

# function to extract information from tags
def extracttaginfo(tag):
    splittag = tag.split("_")
    if splittag[0]==("node") or splittag[0]==("bridge"):
        # return [x, y, z]
        strtag = splittag[1:4]
        numtags = 3
    # for all other cases
    else:
        # return [x0, y0, x, y]
        strtag = splittag[1:5]
        numtags = 4
    # create empty array to store floats
    floattag = [0] * numtags
    # convert to float
    for i in range(numtags):
        floattag[i] = float(strtag[i])
    return floattag

# extract all line information
def extractlines(taglist):
    # this will contain the mathematically defined lines
    # [xbound, ybound, slope]
    lines = []
    for line in taglist:
        linecoords = extracttaginfo(line)
        lines.append(defineline(linecoords[0],linecoords[2],linecoords[1],linecoords[3]))
    return lines

# extract 3D coordinate information from tags
def extractcoords():
    # initialize a bridge counter
    bridgeloc = []
    numtags = len(nodetags)
    coords=[[0,0,0]]*(numtags+2)
    for c in range(numtags):
        coords[c+1]=extracttaginfo(nodetags[c])
        # check if the tag is a bridge
        if coords[c+1][2] == bridgeheight:
            #print("bridge detected!")
            bridgeloc.append(c+1)
    # iterate through array and insert bridge elements
    for b in range(len(bridgeloc)):
        bridgetag = extracttaginfo(bridgetags[b])
        loc = bridgeloc[b]+(4*(b))
        # need to determine which end of the bridge falls first
        # TODO this is still not working
        prevnode = coords[loc-1] #x,y,z
        distance1 = np.sqrt((np.abs(prevnode[0])-np.abs(bridgetag[0]))**2+(np.abs(prevnode[1])-np.abs(bridgetag[2]))**2)
        distance2 = np.sqrt((np.abs(prevnode[0])-np.abs(bridgetag[1]))**2+(np.abs(prevnode[1])-np.abs(bridgetag[3]))**2)
        if distance1 < distance2:
            bridgestart = [bridgetag[0],bridgetag[2]]
            bridgeend = [bridgetag[1],bridgetag[3]]
        else:
            bridgestart = [bridgetag[1],bridgetag[3]]
            bridgeend = [bridgetag[0],bridgetag[2]]
        coords.insert(loc,[bridgestart[0],bridgestart[1],0])
        coords.insert(loc+1,[bridgestart[0],bridgestart[1],bridgeheight])
        coords.insert(loc+3,[bridgeend[0],bridgeend[1],bridgeheight])
        coords.insert(loc+4,[bridgeend[0],bridgeend[1],0])
    # add a bridge to first and last node so that closure goes below everything else
    if numtags > 1:
        # first copy first and last node
        coords[0] = extracttaginfo(nodetags[0])
        coords[-1] = extracttaginfo(nodetags[numtags-1])
        # then change the z to a positive higher value
        coords[0][2]=2.
        coords[-1][2]=2.
    return coords

# check particular line for intersections against all other lines
# takes in the array of lines produced in extractlines()
def checklines(linearray, lineofinterest):
    # this will contain intersection coordinates
    # [xintersect, yintersect]
    intersections = []
    for line in linearray:
        # we don't want a line to find intersections with itself
        if line == lineofinterest:
            intersect = None
        else:
            # otherwise we check for intersections with all other lines
            # in the future we may want to implement a limit on which lines to check
            intersect = checkintersect(line[0],lineofinterest[0],line[1],lineofinterest[1],line[2],lineofinterest[2])
        # add an intersection if it exists
        if intersect != None:
            intersections.append(intersect)
    return intersections

# function to draw nodes
def drawnode(x, y, z, radius, color, type="node", activecolor=nodecolor):
    tag = type + "_" + str(x) + "_" + str(y) + "_" + str(z)
    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, activefill=activecolor, width=0, tags=tag)
    nodetags.append(tag)
#    if type == "node":
#        nodetags.append(tag)
#    elif type == "bridge":
#        bridgetags.append(tag)

def drawline(x0, y0, x, y, thickness, color, type="line", bridgeinfo = None):
    # we need to make closuretag global to modify it here
    global  closuretag
    tag = type + "_" + str(x0) + "_" + str(x) + "_" + str(y0) + "_" + str(y)
    canvas.create_line(x0, y0, x, y, fill = color, width = thickness, tags=tag)
    if type == "line":
        linetags.append(tag)
        drawintersections(x0, y0, x, y)
    elif type == "closure":
        closuretag = tag
#        drawintersections(x0, y0, x, y)
    elif type == "bridgeline":
        tag += "_node_"+str(bridgeinfo[0])+"_"+str(bridgeinfo[1])+"_"+str(bridgeinfo[2])
        bridgetags.append(tag)

# main drawing function
def drawsegment(x,y):
    # number of nodes
    numnodes = len(nodetags)
    # check if there is an initial node
    if numnodes!=0:
        # use use the coordinates of the previous node
        previousnode = extracttaginfo(nodetags[-1])
        drawline(previousnode[0],previousnode[1],x,y,linethickness,linecolor)

        drawnode(x,y,0,noderadius,nodecolor)
        # raise the nodes to the top of the canvas so they are drawn over the lines
        canvas.tag_raise(nodetags[-1])
        canvas.tag_raise(nodetags[numnodes-1])
    # otherwise just draw the initial node
    else:
        drawnode(x,y,0,noderadius,nodecolor)

def drawclosure():
    # delete previous closure line if it exists
    if closuretag != None:
        canvas.delete(closuretag)
    # check if there are at least three nodes so that a closure line is appropriate
    if len(nodetags) > 2:
        # find coordinates of first node
        firstnode = extracttaginfo(nodetags[0])
        lastnode = extracttaginfo(nodetags[-1])
        drawline(firstnode[0],firstnode[1],lastnode[0],lastnode[1],linethickness,closurecolor,type="closure")

def drawbridge(x,y,z,slope):
    drawnode(x,y,z,noderadius,canvasbackground,type="bridge",activecolor=activenode)
    bridge = definebridge(x,y,slope,noderadius,bridgeheight)
    drawline(bridge[0][0],bridge[1][0],bridge[0][1],bridge[1][1],linethickness,linecolor,type="bridgeline",bridgeinfo=[x,y,z])

def drawintersections(x0, y0, x, y, type="line"):
    # define the line we are checking for intersections
    drawnline = defineline(x0, y0, x, y)
    # extract all other line data
    lines=extractlines(linetags)
    # check for intersections
    intersections = checklines(lines, drawnline)
#    if type == "line":
#        color = linecolor
#    elif type == "closure":
#        color = closurecolor
    # draw a bridge for each intersection
    for i in intersections:
        drawbridge(i[0],i[1],bridgeheight,drawnline[2])
# just for testing
import numpy as np
from pyknotid.spacecurves import Knot

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
        drawclosure()
        coordinates = extractcoords()
        ncoords = np.array(coordinates)
        print(ncoords)
        k = Knot(ncoords)
        k.plot(mode='matplotlib')
        print("bridges")
        print(bridgetags)


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
canvas.bind("<Button-1>", canvasinteract, add="+")
canvas.bind("<Button-3>", drawbridge, add="+")

# begin progam main loop
root.mainloop()
