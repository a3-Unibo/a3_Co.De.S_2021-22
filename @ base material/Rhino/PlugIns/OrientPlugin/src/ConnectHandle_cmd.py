import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino
from Rhino.Commands import *
from scriptcontext import doc

__commandname__ = "ConnectHandle"

def ptsFromPolyline(poly=None):
    if poly==None: return
    pts = rs.PolylineVertices(poly)
    
    if len(pts) != 3:
        return
    newPts = []
    newPts.append(pts[1])
    newPts.append(pts[0])
    newPts.append(pts[2])
    return newPts
    
def planeFromPts(pts=None):
    if pts==None: return
    plane = rs.PlaneFromPoints(pts[1],pts[0],pts[2])
    return plane
    
def RhinoUpdateObjectGroups(obj, group_map):
    if obj == None: return
    attrib_group_count = obj.Attributes.GroupCount
    if attrib_group_count == 0: return

    doc = obj.Document
    if doc == None: return

    groups = doc.Groups

    group_count = groups.Count
    if group_count == 0: return

    if group_map.Count == 0:
        for i in range(0, group_count):
            group_map.append(-1)

    attributes = obj.Attributes
    group_list = attributes.GetGroupList()
    if group_list == None: return
    attrib_group_count = group_list.Length

    for i in range(0, attrib_group_count):
        old_group_index = group_list[i]
        new_group_index = group_map[old_group_index]
        if new_group_index == -1:
            new_group_index = doc.Groups.Add()
            group_map[old_group_index] = new_group_index
        group_list[i] = new_group_index

    attributes.RemoveFromAllGroups()
    for i in range(0, attrib_group_count):
        attributes.AddToGroup(group_list[i])

    obj.CommitChanges()

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
    # get input objects
    objs = rs.GetObjects("Select object(s) to connect")
    if (objs is None):
        return 1
    # select source handle
    source = rs.GetObject("Select sender handle (L polyline)", rs.filter.curve)
    if(source is None):
       return 1
    sPoly = rs.coercecurve(source)

    # select destination handle
    receiver = rs.GetObject("Select receiver handle (L polyline)", rs.filter.curve)
    if (receiver is None):
        return 1
    rPoly = rs.coercecurve(receiver)
    
    if not(rs.IsPolyline(sPoly) & rs.IsPolyline(rPoly)): return 1
    
    preview = []
    while True:
        # input rotation angle
        rotation = rs.GetReal("Rotation angle (degrees)",0,-360,360)
        if rotation is None: break
        rs.EnableRedraw(False)
        
        # precalculate points, planes and transformation
        sPts = ptsFromPolyline(sPoly)
        rPts = ptsFromPolyline(rPoly)
        sPlane = planeFromPts(sPts)
        rPlane = planeFromPts(rPts)
        origin = rPts[0]
        rPts = rs.RotateObjects(rPts, origin,180,rPlane.YAxis)
        rPts1 = rs.RotateObjects(rPts, origin,-rotation,rPlane.ZAxis)
        for obj in objs:
            preview.append(rs.OrientObject(obj,sPts,rPts1,1))

        rs.DeleteObjects(rPts1)
        rs.EnableRedraw(True)
        result = rs.GetString("Looks good?", "Yes", ("Yes", "No"))
        if result is None:
            rs.EnableRedraw(False)
            for obj in preview: rs.DeleteObject(obj)
            rs.EnableRedraw(True)
            break
        result = result.upper()
        if result=="YES":
            group_map = []
            for obj in preview:
                obj = rs.coercerhinoobject(obj)
                RhinoUpdateObjectGroups(obj, group_map)
            break
        elif result=="NO":
            rs.EnableRedraw(False)
            for obj in preview: rs.DeleteObject(obj)
            rs.EnableRedraw(True)

    # you can optionally return a value from this function
    # to signify command result. Return values that make
    # sense are
    #   0 == success
    #   1 == cancel
    # If this function does not return a value, success is assumed
    return 0


RunCommand(True)