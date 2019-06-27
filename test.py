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
