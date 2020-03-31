import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import numpy as np
import pyknotid
import pyknotid.spacecurves as pkidsc
from pyknotid.spacecurves import Knot
import sympy
import csv
import os

# set initial values
gc_str = ""
fileopen = False
t = sympy.Symbol("t")  # for use in displaying polynomial invariant

### GENERAL FUNCTIONS ###

# determine equation of line
def defineline(x1, y1, x2, y2):
    xbound = [x1, x2]
    ybound = [y1, y2]
    if x1 == x2:
        slope = None
    else:
        slope = (y2 - y1) / (x2 - x1)
    return [xbound, ybound, slope]


# find the y-intercept of a given line
def findyintercept(x, y, m):
    b = y - (m * x)
    return b


# check if intersect between two lines falls within their range
def checkrange(xbound1, xbound2, ybound1, ybound2, intersect):
    line1x, line2x, line1y, line2y = [False] * 4
    # check xrange of first line
    if intersect[0] > min(xbound1) and intersect[0] < max(xbound1):
        line1x = True
    # check x range of second line
    if intersect[0] > min(xbound2) and intersect[0] < max(xbound2):
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
def checkintersect(xbound1, xbound2, ybound1, ybound2, slope1, slope2):
    # check if line 1 is vertical
    if slope1 == None:
        # in this case, the two lines intersect everwhere
        if slope2 == None:
            # not correct but sufficient for the purposes of this script
            return None
        # otherwise, only line 1 is vertical
        else:
            b2 = findyintercept(xbound2[0], ybound2[0], slope2)
            xintersect = xbound1[0]
            yintersect = slope2 * xintersect + b2
            # check if intersect in range
            if (
                checkrange(xbound1, xbound2, ybound1, ybound2, [xintersect, yintersect])
                == True
            ):
                return [xintersect, yintersect]
            else:
                return None
    # check if line 2 is vertical
    elif slope2 == None:
        # previous conditial checked if line 1 was vertical
        b1 = findyintercept(xbound1[0], ybound1[0], slope1)
        xintersect = xbound2[0]
        yintersect = slope1 * xintersect + b1
        # check if intersect in range
        if (
            checkrange(xbound1, xbound2, ybound1, ybound2, [xintersect, yintersect])
            == True
        ):
            return [xintersect, yintersect]
        else:
            return None
    # if neither line is vertical
    else:
        b1 = findyintercept(xbound1[0], ybound1[0], slope1)
        b2 = findyintercept(xbound2[0], ybound2[0], slope2)
        xintersect = (b2 - b1) / (slope1 - slope2)
        yintersect = slope1 * xintersect + b1
        # check if intersect in range
        if (
            checkrange(xbound1, xbound2, ybound1, ybound2, [xintersect, yintersect])
            == True
        ):
            return [xintersect, yintersect]
        else:
            return None


# determine which lines to check for intersection
# this function ignores the end point of the lines which is good for our purposes
# I am not sure if this is computationally more efficient than just checking for
# intersections with every line
def potentialintersection(xbound, ybound, linearray):
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


# determine which of point in an array is closer to the point of interest
def pythagdistance(x0, y0, points):
    # points should be an array of [x,y] coordinates
    distlist = []
    for p in points:
        distlist.append(
            np.sqrt((np.abs(x0) - np.abs(p[0])) ** 2 + (np.abs(y0) - np.abs(p[1])) ** 2)
        )
    return points[distlist.index(min(distlist))]


def pythag(x0, y0, x, y):
    distance = np.sqrt((np.abs(x0) - np.abs(x)) ** 2 + (np.abs(y0) - np.abs(y)) ** 2)
    return distance


# define bounds of bridge
def definebridge(xintersect, yintersect, slope, x0, y0, radius, bridgeheight):
    # slope represents the top line
    # if top line is vertical
    if slope == None:
        x = 0
        y = radius
    # else if top line has an angle from vertical
    else:
        # find angle from slope
        angle = np.arctan(slope)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
    # now we need to use pythagorean theorem to determine which end of the bridge to
    # start drawing
    edge1 = [xintersect - x, yintersect - y]
    edge2 = [xintersect + x, yintersect + y]
    closeedge = pythagdistance(x0, y0, [edge1, edge2])
    if closeedge == edge1:
        bridge = [[edge1[0], edge2[0]], [edge1[1], edge2[1]], bridgeheight]
    else:
        bridge = [[edge2[0], edge1[0]], [edge2[1], edge1[1]], bridgeheight]
    return bridge


### DRAWING ###

# initialize lists to hold tags canvas elements
nodetags = []  # x, y
bridgetags = []  # xbounds, ybounds, (z?)
linetags = []  # xbounds, ybounds, (slope?)
closuretag = None  # xbounds, ybounds

# graphical variables
#canvasbackground = "#d9d9d9"
canvasbackground = "#ffffff"
noderadius = 5
nodecolor = "#ce0000"
linethickness = 2
linecolor = "#5a79a5"
closurecolor = "#96439d"
activenode = "#000000"
bridgeheight = 1

# function to extract information from tags
def extracttaginfo(tag):
    splittag = tag.split("_")
    if splittag[0] == ("node") or splittag[0] == ("bridge"):
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
        lines.append(
            defineline(linecoords[0], linecoords[2], linecoords[1], linecoords[3])
        )
    return lines


# extract 3D coordinate information from tags
# def extractcoords():
#    # initialize a bridge counter
#    bridgeloc = []
#    numtags = len(nodetags)
#    coords=[[0,0,0]]*(numtags+2)
#    for c in range(numtags):
#        coords[c+1]=extracttaginfo(nodetags[c])
#        # check if the tag is a bridge
#        if coords[c+1][2] == bridgeheight:
#            #print("bridge detected!")
#            bridgeloc.append(c+1)
#    # iterate through array and insert bridge elements
#    for b in range(len(bridgeloc)):
#        bridgetag = extracttaginfo(bridgetags[b])
#        loc = bridgeloc[b]+(4*(b))
#        bridgestart= [bridgetag[0],bridgetag[2]]
#        bridgeend=[bridgetag[1],bridgetag[3]]
#        coords.insert(loc,[bridgestart[0],bridgestart[1],0])
#        coords.insert(loc+1,[bridgestart[0],bridgestart[1],bridgeheight])
#        coords.insert(loc+3,[bridgeend[0],bridgeend[1],bridgeheight])
#        coords.insert(loc+4,[bridgeend[0],bridgeend[1],0])
#    # add a bridge to first and last node so that closure goes below everything else
#    if numtags > 1:
#        # first copy first and last node
#        coords[0] = extracttaginfo(nodetags[0])
#        coords[-1] = extracttaginfo(nodetags[numtags-1])
#        # then change the z to a positive higher value
#        coords[0][2]=2.
#        coords[-1][2]=2.
#    return coords

# extract 3D coordinates from tags v2.0
def extractcoordinates():
    # initialize a bridge counter
    bridgeloc = []
    numtags = len(nodetags)
    coords = [[0, 0, 0]] * (numtags + 2)
    for c in range(numtags):
        coords[c + 1] = extracttaginfo(nodetags[c])
        # check if tag is a bridge
        if coords[c + 1][2] == bridgeheight:
            bridgeloc.append(c + 1)
    # iterate through array and insert bridge elements
    for b in range(len(bridgeloc)):
        loc = bridgeloc[b] + (4 * (b))
        prevnode = coords[loc - 1]  # x,y,z
        nextnode = coords[loc + 1]
        slope = defineline(prevnode[0], prevnode[1], nextnode[0], nextnode[1])[2]
        tempbridge = definebridge(
            coords[loc][0],
            coords[loc][1],
            slope,
            prevnode[0],
            prevnode[1],
            noderadius,
            bridgeheight,
        )
        x1 = tempbridge[0][0]
        x2 = tempbridge[0][1]
        y1 = tempbridge[1][0]
        y2 = tempbridge[1][1]
        bridge1 = [x1, y1, 0]
        bridge2 = [x1, y1, 1]
        bridge3 = [x2, y2, 1]
        bridge4 = [x2, y2, 0]
        coords.insert(loc, bridge1)
        coords.insert(loc + 1, bridge2)
        coords.insert(loc + 3, bridge3)
        coords.insert(loc + 4, bridge4)
    # add a bridge to first and last node so that closure goes below everything else
    if numtags > 1:
        # first copy first and last node
        coords[0] = extracttaginfo(nodetags[0])
        coords[-1] = extracttaginfo(nodetags[numtags - 1])
        # then change the z to a positive higher value
        coords[0][2] = 2.0
        coords[-1][2] = 2.0
    return coords


# check particular line for intersections against all other lines
# takes in the array of lines produced in extractlines()
def checklines(linearray, lineofinterest):
    # this will contain intersection coordinates
    # [xintersect, yintersect]
    intersections = []
    for line in linearray:
        intersect = checkintersect(
            line[0],
            lineofinterest[0],
            line[1],
            lineofinterest[1],
            line[2],
            lineofinterest[2],
        )
        # we don't want a line to find intersections with itself
        # if line == lineofinterest:
        #    intersect = None
        # else:
        # otherwise we check for intersections with all other lines
        # in the future we may want to implement a limit on which lines to check
        #    intersect = checkintersect(line[0],lineofinterest[0],line[1],lineofinterest[1],line[2],lineofinterest[2])
        # add an intersection if it exists
        if intersect != None:
            intersections.append(intersect)
    return intersections


# function to draw nodes
def drawnode(x, y, z, radius, color, type="node", activecolor=nodecolor):
    tag = type + "_" + str(x) + "_" + str(y) + "_" + str(z)
    canvas.create_oval(
        x - radius,
        y - radius,
        x + radius,
        y + radius,
        fill=color,
        activefill=activecolor,
        width=0,
        tags=tag,
    )
    nodetags.append(tag)


def drawline(x0, y0, x, y, thickness, color, type="line", bridgeinfo=None):
    # we need to make closuretag global to modify it here
    global closuretag
    tag = type + "_" + str(x0) + "_" + str(x) + "_" + str(y0) + "_" + str(y)
    canvas.create_line(x0, y0, x, y, fill=color, width=thickness, tags=tag)
    if type == "line":
        linetags.append(tag)
        drawintersections(x0, y0, x, y)
    elif type == "closure":
        closuretag = tag
    #        drawintersections(x0, y0, x, y)
    elif type == "bridgeline":
        tag += (
            "_node_"
            + str(bridgeinfo[0])
            + "_"
            + str(bridgeinfo[1])
            + "_"
            + str(bridgeinfo[2])
        )
        bridgetags.append(tag)


# main drawing function
def drawsegment(x, y):
    # number of nodes
    numnodes = len(nodetags)
    # check if there is an initial node
    if numnodes != 0:
        # use use the coordinates of the previous node
        previousnode = extracttaginfo(nodetags[-1])
        drawline(previousnode[0], previousnode[1], x, y, linethickness, linecolor)

        drawnode(x, y, 0, noderadius, nodecolor)
        # raise the nodes to the top of the canvas so they are drawn over the lines
        canvas.tag_raise(nodetags[-1])
        canvas.tag_raise(nodetags[numnodes - 1])
    # otherwise just draw the initial node
    else:
        drawnode(x, y, 0, noderadius, nodecolor)


def drawclosure():
    # delete previous closure line if it exists
    if closuretag != None:
        canvas.delete(closuretag)
    # check if there are at least three nodes so that a closure line is appropriate
    if len(nodetags) > 2:
        # find coordinates of first node
        firstnode = extracttaginfo(nodetags[0])
        lastnode = extracttaginfo(nodetags[-1])
        drawline(
            firstnode[0],
            firstnode[1],
            lastnode[0],
            lastnode[1],
            linethickness,
            closurecolor,
            type="closure",
        )


def drawbridge(x, y, z, x0, y0, slope):
    drawnode(
        x, y, z, noderadius, canvasbackground, type="bridge", activecolor=activenode
    )
    bridge = definebridge(x, y, slope, x0, y0, noderadius, bridgeheight)
    drawline(
        bridge[0][0],
        bridge[1][0],
        bridge[0][1],
        bridge[1][1],
        linethickness,
        linecolor,
        type="bridgeline",
        bridgeinfo=[x, y, z],
    )


def drawintersections(x0, y0, x, y, type="line"):
    # define the line we are checking for intersections
    drawnline = defineline(x0, y0, x, y)
    # extract all other line data
    lines = extractlines(linetags[:-2])
    # check for intersections
    intersections = checklines(lines, drawnline)
    #    if type == "line":
    #        color = linecolor
    #    elif type == "closure":
    #        color = closurecolor
    intersectnumber = len(intersections)
    orderedintersects = [0] * intersectnumber
    # check which intersection should fall first
    for i in range(intersectnumber):
        # first closest
        closestintersect = pythagdistance(x0, y0, intersections)
        # append to ordered list
        orderedintersects[i] = closestintersect
        # delete from initial intersection list
        del intersections[intersections.index(closestintersect)]

    # draw a bridge for each intersection
    for i in orderedintersects:
        drawbridge(i[0], i[1], bridgeheight, x0, y0, drawnline[2])


def canvasinteract(event):
    global knot
    global coordinates
    global coordarray

    # capture mouse location
    x, y = event.x, event.y
    # this is the size of the bounding box for determining intersections
    # this also is the region in which you cannot draw another node conveniently
    hbsize = 10
    tags = []
    lines = []
    # this should contain four elements: bridge node, bridge line and two intersecting
    # lines
    points = canvas.find_overlapping(
        x - hbsize / 2, y - hbsize / 2, x + hbsize / 2, y + hbsize / 2
    )
    for p in points:
        # this returns a tuple so we only want the first element of each tag
        # we only use one tag per item on this canvas
        tags.append(canvas.gettags(p)[0])
    # check if anything was enclosed
    if len(tags) > 0:
        for tag in tags:
            splittag = extracttaginfo(tag)
            if tag.split("_")[0] == ("line"):
                # x0,x,y0,y
                lines.append(
                    defineline(splittag[0], splittag[2], splittag[1], splittag[3])
                )
            if tag.split("_")[0] == ("bridge"):
                # x,y,z
                bridgenode = extracttaginfo(tag)
                nodeb = tag
                bridgenodeposition = nodetags.index(tag)
            if tag.split("_")[0] == ("bridgeline"):
                # this is inefficient and could be remedied by fixing the tag order in
                # drawline
                for btag in bridgetags:
                    if btag.startswith(tag):
                        # x0,y0,x,y
                        origbridgetag = extracttaginfo(btag)
                        bridge = [
                            [origbridgetag[0], origbridgetag[1]],
                            [origbridgetag[2], origbridgetag[3]],
                        ]
                        # tag location in array of bridge tags
                        tagloc = bridgetags.index(btag)
                        # remove previous bridge from canvas
                        canvas.delete(tag)
                        # the bridge line is deleted but its tag still exists
                        # we still have a list of 4 elements
                        # want to calculate the bridge about the node using the two
                        # lines
                        # we calculate both potential bridges manually
                        # returns [[x0,x],[y0,y],z]
                        bridge1 = definebridge(
                            bridgenode[0],
                            bridgenode[1],
                            lines[0][2],
                            lines[0][0][0],
                            lines[0][1][0],
                            noderadius,
                            bridgeheight,
                        )[:-1]
                        bridge2 = definebridge(
                            bridgenode[0],
                            bridgenode[1],
                            lines[1][2],
                            lines[1][0][0],
                            lines[1][1][0],
                            noderadius,
                            bridgeheight,
                        )[:-1]
                        # these are the potential initial nodes which we will need to
                        # find start and end of the two intersection lines
                        node1 = (
                            "node_"
                            + str(int(lines[0][0][0]))
                            + "_"
                            + str(int(lines[0][1][0]))
                            + "_"
                            + "0"
                        )
                        node2 = (
                            "node_"
                            + str(int(lines[1][0][0]))
                            + "_"
                            + str(int(lines[1][1][0]))
                            + "_"
                            + "0"
                        )
                        # delete old bridge node
                        del nodetags[bridgenodeposition]
                        # find the array position of each of these
                        node1loc = nodetags.index(node1)
                        node2loc = nodetags.index(node2)
                        # iterate through bridges after line starts
                        bridgedist1 = pythag(
                            lines[0][0][0], lines[0][1][0], bridgenode[0], bridgenode[1]
                        )
                        n = 1
                        while nodetags[node1loc + n].split("_")[0] == "bridge":
                            otherbridgedist = pythag(
                                lines[0][0][0],
                                lines[0][1][0],
                                float(nodetags[node1loc + n].split("_")[1]),
                                float(nodetags[node1loc + n].split("_")[2]),
                            )
                            if otherbridgedist > bridgedist1:
                                break
                            if nodetags[node1loc + n].split("_")[0] != "bridge":
                                break
                            n += 1
                        bridgedist2 = pythag(
                            lines[1][0][0], lines[1][1][0], bridgenode[0], bridgenode[1]
                        )
                        m = 1
                        while nodetags[node2loc + m].split("_")[0] == "bridge":
                            otherbridgedist = pythag(
                                lines[1][0][0],
                                lines[1][1][0],
                                float(nodetags[node2loc + m].split("_")[1]),
                                float(nodetags[node2loc + m].split("_")[2]),
                            )
                            if otherbridgedist > bridgedist2:
                                break
                            if nodetags[node2loc + m].split("_")[0] != "bridge":
                                break
                            m += 1
                        # we want the new bridge, not a duplicate of the old one
                        nodepart = (
                            "_node_"
                            + str(bridgenode[0])
                            + "_"
                            + str(bridgenode[1])
                            + "_"
                            + str(bridgenode[2])
                        )
                        if bridge1 == bridge:
                            newtag = (
                                "bridgeline_"
                                + str(bridge2[0][0])
                                + "_"
                                + str(bridge2[0][1])
                                + "_"
                                + str(bridge2[1][0])
                                + "_"
                                + str(bridge2[1][1])
                            )
                            # draw bridge2
                            canvas.create_line(
                                bridge2[0][0],
                                bridge2[1][0],
                                bridge2[0][1],
                                bridge2[1][1],
                                fill=linecolor,
                                width=linethickness,
                                tags=newtag,
                            )
                            # find the related node
                            # index = nodetags.index(node2)
                            # delete old bridge node
                            # del(nodetags[bridgenodeposition])
                            # find related node
                            # index = nodetags.index(node2)
                            # insert new bridge node
                            nodetags.insert(node2loc + m, nodeb)
                        elif bridge2 == bridge:
                            newtag = (
                                "bridgeline_"
                                + str(bridge1[0][0])
                                + "_"
                                + str(bridge1[0][1])
                                + "_"
                                + str(bridge1[1][0])
                                + "_"
                                + str(bridge1[1][1])
                            )
                            # index = nodetags.index(node1)
                            # delete old bridge node
                            # del(nodetags[bridgenodeposition])
                            # index=nodetags.index(node1)
                            # insert new bridge node
                            # draw bridge
                            canvas.create_line(
                                bridge1[0][0],
                                bridge1[1][0],
                                bridge1[0][1],
                                bridge1[1][1],
                                fill=linecolor,
                                width=linethickness,
                                tags=newtag,
                            )
                            nodetags.insert(node1loc + n, nodeb)
                        else:
                            print("something went wrong")
                        # replace the tag for the old bridge
                        bridgetags[tagloc] = newtag + nodepart
    elif len(tags) > 4:
        print("Too many overlapping elements for program to distinguish")
    # otherwise just draw a new line segment
    else:
        drawsegment(x, y)
        drawclosure()
        # print(ncoords)
        # k = Knot(ncoords)
        # k.plot(mode='matplotlib')
        # print("bridges")
        # print(bridgetags)
    # convert in pyknotid knot object
    coordinates = extractcoordinates()
    coordarray = np.array(coordinates)
    knot = Knot(coordarray)


### ANALYSIS
def findgausscode(event):
    global gc
    #    global k
    if len(coordinates) > 1:
        gc = knot.identify()
        # simplify the gauss code
        #gc.simplify()
        # display gauss code
        gcode.config(text=str(gc))


def clearcanvas(event):
    global nodetags, bridgetags, linetags, coordinates, coordarray, closuretag, knot
    canvas.delete("all")
    nodetags = []  # x, y
    bridgetags = []  # xbounds, ybounds, (z?)
    linetags = []  # xbounds, ybounds, (slope?)
    coordinates = []
    coordarray = []
    closuretag = None  # xbounds, ybounds
    knot = None


def displayrealtime(event):
    x, y = event.x, event.y
    coords = str(x) + ", " + str(y)
    coordsrealtime.config(text=coords)


def closewindow():
    window.destroy()


# clear clipboard and copy the currently displayed gauss code
def copygauss(event):
    root.clipboard_clear()
    root.clipboard_append(gc_str)


# open file to save data:
def openfile(event):
    global numknots
    global fileopen
    # set number of entries to -1 initially so we don't count the header
    numknots = -1
    root.filename = fd.askopenfilename(
        initialdir="/",
        title="Select file",
        filetypes=[("    comma-separated values", ".csv")],
    )
    filename.config(text=root.filename.split("/")[-1])
    fileopen = True
    # update numknots NEEDS TESTING
    with open(root.filename, newline="") as csvfile:
        knotentries = csv.reader(csvfile, delimiter=" ", quotechar="|")
        for row in knotentries:
            numknots += 1
    entries.config(text=str(numknots) + " entries")


# new file to save data to
def newfile(event):
    global numknots
    global fileopen
    # ask for new filename and location
    root.filename = fd.asksaveasfilename(
        initialdir="/", title="New file", defaultextension=".csv"
    )
    # make file
    with open(root.filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["gauss", "crossingnum", "alexander"])
    # update filename
    filename.config(text=root.filename.split("/")[-1])
    fileopen = True
    # set number of knots to 0
    numknots = 0
    entries.config(text=str(numknots) + " entries")


def writedata(event):
    global numknots
    if fileopen == True:
        # update number of knots
        numknots = numknots + 1
        entries.config(text=str(numknots) + " entries")
        # check if knot directory exists and creates it if not
        jsonpath = root.filename[:-4] + "_json"
        if os.path.exists(jsonpath) != True:
            os.makedirs(jsonpath)
        # save knot coordinate data to json file
        knot.to_json(jsonpath + "/" + str(numknots) + ".json")
        # write knot analysis to csv
        with open(root.filename, "a") as f:
            writer = csv.writer(f)
            writer.writerow(
                [str(gc), len(gc), str(knot.alexander_polynomial(variable=t))]
            )
    else:
        mb.showerror(
            "Error", "No active file. Open a file or start a new file to save data."
        )

def editdata(event):
    global numknots
    if fileopen == True:
        # check if there is at least one knot
        if numknots == 0:
            mb.showerror(
                "Error","This file has no knots to edit."
            )
        else:
            # check if the knot listed in edit field exists
            mknot = modknot.get()
            if int(mknot) > numknots:
                mb.showerror(
                    "Error","You are trying to edit a knot that does not exist."
                )
            else:
                # check if json data for old knot exists
                jsonpath = root.filename[:-4] + "_json/" + mknot + ".json"
                if os.path.exists(jsonpath):
                    # delete old json file
                    os.remove(jsonpath)
                    knot.to_json(jsonpath)
                else:
                    # save knot coordinate data to json file
                    knot.to_json(jsonpath)
                # update knot analysis in csv
                # read current file
                with open(root.filename, "r") as f:
                    knotreader = csv.reader(f)
                    rows = []
                    for row in knotreader:
                        rows.append(row)
                # remove original file
                os.remove(root.filename)
                # recreate file to reload knots
                with open(root.filename, "a") as f:
                    knotwriter = csv.writer(f)
                    nrow = 0
                    for row in rows:
                        nrow += 1
                        # check if this is the knot we want to modify and modify it
                        if nrow == int(mknot) + 1:
                            knotwriter.writerow(
                                [str(gc), len(gc), str(knot.alexander_polynomial(variable=t))]
                            )
                        else:
                            # otherwise just write normal knot
                            knotwriter.writerow(row)
                # delete value in entry field 
                modknot.delete(0,'end')
    else:
        mb.showerror(
            "Error", "No active file. Open a file that you want to edit."
        )

def addunknot(event):
    global numknots
    if fileopen == True:
        # update number of knots
        numknots = numknots + 1
        entries.config(text=str(numknots) + " entries")
        # write knot analysis to csv
        with open(root.filename, "a") as f:
            writer = csv.writer(f)
            writer.writerow(["nil", 0, "nil"])
    else:
        mb.showerror(
            "Error", "No active file. Open a file or start a new file to save data."
        )

def addcomplex(event):
    global numknots
    if fileopen == True:
        # update number of knots
        numknots = numknots + 1
        entries.config(text=str(numknots) + " entries")
        # write knot analysis to csv
        with open(root.filename, "a") as f:
            writer = csv.writer(f)
            writer.writerow(["complex", 99, "complex"])
    else:
        mb.showerror(
            "Error", "No active file. Open a file or start a new file to save data."
        )

def popuphelp(event):
    mb.showinfo(
        "Help",
        "A wrapper which allows graphical input of knots to be analyzed with pyknotid.\nYou can open a previous csv file or start a new one and then draw your knot. The closure option doesn't change the analysis. It only affects the appearance. Upon saving (w), the knot coordinates are saved as a json file in a subfolder created by the program in the working directory. The analysis details are also appended to the csv. The canvas can be cleared (c) and the program can be closed easily (q).\nCreated by Xavier and Luc Capaldi and released with the MIT License (c) 2019. ",
    )


def popupmoo(event):
    mb.showwarning(
        "Moo",
        "    -----------\n< whyknot >\n    -----------\n        \   ^__^\n         \  (oo)\_______\n            (__)\           )\/\ \n                  ||-----w |\n                  ||        ||",
    )


# CAN USE activefill to show when switching
# can also use canvas.config(cursor="exchange")

### TKINTER ###

# create main window
root = tk.Tk()
root.title("WhyKnot")
root.geometry("1280x720")
root.wait_visibility(root)
root.wm_attributes('-alpha',1.0)

# create main frames within the root frame
drawframe = tk.Frame(root, width=980, height=720)
interfaceframe = tk.Frame(root, width=300, height=720)

# set geometry manager class for main frames and organize within root frame
drawframe.grid(column=0, row=0, sticky="nsw")
interfaceframe.grid(column=1, row=0, sticky="nse")

# create canvas widget for draw frame
canvas = tk.Canvas(
    drawframe, bg=canvasbackground, cursor="cross", width=980, height=720
)

# place widget in draw frame
canvas.grid(row=0, column=0)

# create widgets for interface frame
title = tk.Label(interfaceframe, text="WhyKnot", font=("Helvetica", 18))

gcodevar = tk.StringVar()  # button var so text can be updated
gcodevar.set("--")
gcode = tk.Label(interfaceframe, text="--", font=("Helvetica", 15), wraplength=300)

file = tk.Button(interfaceframe, text="File")
new = tk.Button(interfaceframe, text="New")
save = tk.Button(interfaceframe, text="Save (w)")
unknot = tk.Button(interfaceframe, text="Unknot (u)")
complexknot = tk.Button(interfaceframe, text="Too Complex (t)")
help = tk.Button(interfaceframe, text="Help")
# results = tk.Label(interface_frame, text="Results Goes Here")
close = tk.Button(interfaceframe, text="Quit (q)")
clear = tk.Button(interfaceframe, text="Clear (c)")
coordsrealtime = tk.Label(interfaceframe, text="--")
filename = tk.Label(interfaceframe, text="no file", font=("Helvetica", 10))
entries = tk.Label(interfaceframe, text="0 entries", font=("Helvetica", 10))
modknot = tk.Entry(interfaceframe)
edit = tk.Button(interfaceframe, text="Edit")

# place widgets in interface frame
title.grid(row=1, columnspan=2)
gcode.grid(row=7, columnspan=2)
# closures.grid(row=5, columnspan=2)
file.grid(row=2, column=0)
new.grid(row=2, column=1)
save.grid(row=3, column=0)
unknot.grid(row=3, column=1)
complexknot.grid(row=4, columnspan=2)
help.grid(row=11, columnspan=2)
filename.grid(row=5, columnspan=2)
entries.grid(row=6, columnspan=2)
clear.grid(row=9, column=0)
close.grid(row=9, column=1)
modknot.grid(row=10, column=0)
edit.grid(row=10, column=1)
coordsrealtime.grid(row=13, columnspan=2)

# event handlers
canvas.bind("<Button-1>", canvasinteract, add="+")
canvas.bind("<Button-1>", findgausscode, add="+")
clear.bind("<Button-1>", clearcanvas)
root.bind("c", clearcanvas)
close.bind("<Button-1>", lambda e: root.destroy())
root.bind("q", lambda e: root.destroy())
root.bind("a", lambda e: root.wm_attributes('-alpha', 0.5))
root.bind("s", lambda e: root.wm_attributes('-alpha', 1.0))
# closures.bind("<Button-1>", include_closures)
# closures.bind("<Button-1>", find_gc)
canvas.bind("<Motion>", displayrealtime)
root.bind("y", copygauss)
save.bind("<Button-1>", writedata)
unknot.bind("<Button-1>", addunknot)
complexknot.bind("<Button-1>", addcomplex)
help.bind("<Button-1>", popuphelp)
root.bind("w", writedata)
edit.bind("<Button-1>", editdata)
root.bind("u", addunknot)
root.bind("t", addcomplex)
file.bind("<Button-1>", openfile)
new.bind("<Button-1>", newfile)
root.bind("m", popupmoo)
root.bind("p", lambda e: knot.plot(mode="matplotlib"))
# begin progam main loop
root.mainloop()
