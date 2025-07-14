import argparse as args
import sys 
import math
import FreeCAD
from FreeCAD import Placement, Rotation, Vector
from freecad import module_io
import FreeCADGui as Gui
import PySide2
import ImportGui
from pyparsing import nestedExpr

#####################################################
# Global parameters for optimization. 
# Please change as necessary.
# Units are in milimeters 

KICAD_3DMODEL_DIR = "C:/Program Files/KiCad/8.0/share/kicad/3dmodels/"
# mac address for Zeyu: "/Users/zeyuyan/Documents/KiCad/8.0/3dmodels/"
# windows address for Suhwan:"C:/Program Files/KiCad/8.0/share/kicad/3dmodels/"

# Minimum trace feature size required for trace segment creation 
# depending on how complex your traces are, this value may have to be 
# decreased or increased. Check trace lenghts in KiCAD to make sure important
# traces are redacted.
MINIMUM_TRACE_LENGTH = 0.5

# Height and Width of the 3D trace segments
DEFAULT_TRACE_HEIGHT = 0.75
DEFAULT_TRACE_WIDTH = 0.75

DEFAULT_LAYER_GAP = 0.25 # Isolation gap between layers

DEFAULT_BODY_OFFSET = 0.3 # Isolation gap from top of body to top of traces

DEFAULT_SOCKET_HEIGHT = 0.05 # Socket insertion depth, no need to change unless necessary

# Enable for a cool animation!
MOVIE_EFFECT = True
REFRESH_RATE = 2 # higher -> less frequent updates

#####################################################
# Do Not Modify
DEFAULT_FCU_Z = DEFAULT_LAYER_GAP - DEFAULT_TRACE_HEIGHT # -0.5
DEFAULT_BCU_Z = DEFAULT_TRACE_HEIGHT - DEFAULT_LAYER_GAP # 0.5
DEFAULT_BODY_FCU_Z = DEFAULT_FCU_Z - DEFAULT_BODY_OFFSET
DEFAULT_BODY_BCU_Z = DEFAULT_BCU_Z + DEFAULT_TRACE_HEIGHT + DEFAULT_BODY_OFFSET
DEFAULT_BODY_HEIGHT = abs(DEFAULT_BODY_BCU_Z) + abs(DEFAULT_BODY_FCU_Z)
DEFAULT_THRUHOLE_HEIGHT = (DEFAULT_TRACE_HEIGHT * 2) + DEFAULT_BODY_OFFSET + DEFAULT_LAYER_GAP
DEFAULT_PAD_HEIGHT = DEFAULT_BODY_OFFSET * 1.05 # Height of pads on top of terminal ends of traces
#####################################################

# Document Settings
DOC_NAME = "PCB_Importing_Example"
DOC = FreeCAD.newDocument(DOC_NAME)
FreeCAD.setActiveDocument(DOC.Name)

# Sets view to include all objects on screen
def set_view():
  """Rearrange View."""
  if not FreeCAD.GuiUp:
      return
  doc = FreeCADGui.ActiveDocument
  if doc is None:
      return
  view = doc.ActiveView
  if view is None:
      return
  # Check if the view is a 3D view:
  if not hasattr(view, "getSceneGraph"):
      return
  view.viewAxometric()
  view.fitAll()

# Collects footprint data from the pcb file,
# grabs component name, footprint, layer, position, then
# returns a list of dictionaries.
# File position is also recorded for ease of iterating
# through the file later on
    #   "name": name,
    #   "footprint": footprint,
    #   "layer": layer,
    #   "x": x,
    #   "y": y,
    #   "r": r,
    #   "filepos": file_pos
def assign_footprints(file: str, ftpt: list):
  with open(file, 'r') as pcbfile:
    line = pcbfile.readline()
    file_pos = pcbfile.tell()
    while line:
      if ("(footprint " in line):
        idx = line.find("\"")
        footprint = line[idx+1:-2]
        # print("Footprint: \t", footprint)

        # Finding Layer 
        layerline = pcbfile.readline()
        idx = layerline.find("\"")
        layer = layerline[idx+1:-3]
        # print("Layer: \t\t", layer)

        # Finding Position
        posline = pcbfile.readline()
        posline = pcbfile.readline()
        posline = posline[5:-2]
        position = posline.split()
        # print("Position: \t", position)
        if (len(position) == 2):
          x, y = map(float, position)
          r = 0
        else:
          x, y, r = map(float, position)

        # Finding Name
        nameline = pcbfile.readline()
        idx = nameline.find("\"Reference\" ")
        while (idx == -1):
          nameline = pcbfile.readline()
          idx = nameline.find("\"Reference\" ")
        name = nameline[idx+13:-2]
        # print(name)
        # print ("----------------------------------------------")

        new_ftpt = {
          "name": name,
          "footprint": footprint,
          "layer": layer,
          "x": x,
          "y": y,
          "r": r,
          "filepos": file_pos
        }

        ftpt.append(new_ftpt)

      # Iterate to next line
      file_pos = pcbfile.tell()
      line = pcbfile.readline()
      
# Collects pad data from the pcb file,
# grabs things like pad type, shape, location, and size.
# Pads can be "smd" or "thru_hole",
# Pad shapes include "rect, roundrect, circle"
# TODO: If there are other pad shapes, it is not supported yet! 
# Update: Added more now..... may still be missing a niche one!
        # (In that case, program will throw up an appropriate error message)
    # "name": name,
    # "number": line[0],
    # "footprint": item['footprint'],
    # "type": line[1]; SMD or Thru_Hole
    # "padtype": line[2]; Rect, Roundrect, Circle, etc. 
    # "x": x, # relative
    # "y": y, # relative
    # "r": r,
    # "padx": padx,
    # "pady": pady,
    # "rratio": rratio / "drill": drill
def assign_pads(file: str, ftpt: list, pads: list):
  with open(file, 'r') as pcbfile:
    for item in ftpt:
        name = item["name"]
        file_pos = item['filepos']
        pcbfile.seek(file_pos)
        line = pcbfile.readline()
        file_pos = pcbfile.tell()

        while line: 
          line = pcbfile.readline()
          if ("pad" in line):
            idx = line.find("\"")
            line = line[idx:-1]
            line = line.replace('\"', '')
            line = line.split()

            # Finding Position
            # Position given seems to be relative to the components!
            # TODO: Should I make the locations abosolute...?
            posline = pcbfile.readline()
            posline = posline[6:-2]
            position = posline.split()
            # print("Position: \t", position)
            if (len(position) == 2):
              x, y = map(float, position)
              r = 0
            else:
              x, y, r = map(float, position)

            # Pad type specifics
            # SMD or thru_hole
            # Rect, Roundrect, Circle

            # SMD Type
            if ("smd" == line[1]):
              if ("rect" == line[2]):
                # print("SMD Pad Type: Roundrect")
                # Parsing size
                sizeline = pcbfile.readline()
                sizeline = sizeline.strip()
                sizeline = sizeline[1:-1]
                sizeline = sizeline.split()
                padx = sizeline[1]
                pady = sizeline[2]

                new_pad = {
                  "name": name,
                  "number": line[0],
                  "footprint": item,
                  "type": line[1],
                  "padtype": line[2],
                  "x": x,
                  "y": y,
                  "r": r,
                  "padx": padx,
                  "pady": pady,
                }

              elif ("roundrect" == line[2]):
                # print("SMD Pad Type: Roundrect")
                # Parsing size
                sizeline = pcbfile.readline()
                sizeline = sizeline.strip()
                sizeline = sizeline[1:-1]
                sizeline = sizeline.split()
                padx = sizeline[1]
                pady = sizeline[2]

                # Parsing Roundrect Ratio 
                rrline = pcbfile.readline()
                rrline = pcbfile.readline()
                rrline = rrline.strip()
                rrline = rrline[1:-1]
                rrline = rrline.split()
                rratio = rrline[1]

                new_pad = {
                  "name": name,
                  "number": line[0],
                  "footprint": item,
                  "type": line[1],
                  "padtype": line[2],
                  "x": x,
                  "y": y,
                  "r": r,
                  "padx": padx,
                  "pady": pady,
                  "rratio": rratio
                }

              elif ("circle" == line[2]):
                print("SMD Pad Type: Circle")
                print("Not yet supported :()")
                sys.exit(1)

            # Thru_Hole Type
            elif ("thru_hole" == line[1]):
              if ("rect" == line[2]):
                # print("Thru_Hole Pad Type: Rect")

                # Parsing size
                sizeline = pcbfile.readline()
                sizeline = sizeline.strip()
                sizeline = sizeline[1:-1]
                sizeline = sizeline.split()
                padx = sizeline[1]
                pady = sizeline[2]

                # Parsing Drill 
                dline = pcbfile.readline()
                dline = dline.strip()
                dline = dline[1:-1]
                dline = dline.split()
                drill = dline[1]

                new_pad = {
                  "name": name,
                  "number": line[0],
                  "footprint": item,
                  "type": line[1],
                  "padtype": line[2],
                  "x": x,
                  "y": y,
                  "r": r,
                  "padx": padx,
                  "pady": pady,
                  "drill": drill
                }

              elif ("roundrect" == line[2]):
                # TODO: May be the same structure as rect 
                # Thru hole pads. May be able to just copy past over?
                print("Thru_Hole Pad Type: Roundrect")
                print("Not yet supported :()")
                sys.exit(1)

              elif ("circle" == line[2]):
                # print("Thru_Hole Pad Type: Circle")

                # Parsing size
                sizeline = pcbfile.readline()
                sizeline = sizeline.strip()
                sizeline = sizeline[1:-1]
                sizeline = sizeline.split()
                padx = sizeline[1]
                pady = sizeline[2]

                # Parsing Drill 
                dline = pcbfile.readline()
                dline = dline.strip()
                dline = dline[1:-1]
                dline = dline.split()
                drill = dline[1]

                new_pad = {
                  "name": name,
                  "number": line[0],
                  "footprint": item,
                  "type": line[1],
                  "padtype": line[2],
                  "x": x,
                  "y": y,
                  "r": r,
                  "padx": padx,
                  "pady": pady,
                  "drill": drill
                }

              elif ("oval" == line[2]):
                # print("Thru_Hole Pad Type: Oval")

                # Parsing size
                sizeline = pcbfile.readline()
                sizeline = sizeline.strip()
                sizeline = sizeline[1:-1]
                sizeline = sizeline.split()
                padx = sizeline[1]
                pady = sizeline[2]

                # Parsing Drill 
                dline = pcbfile.readline()
                dline = dline.strip()
                dline = dline[1:-1]
                dline = dline.split()
                drill = dline[1]

                new_pad = {
                  "name": name,
                  "number": line[0],
                  "footprint": item,
                  "type": line[1],
                  "padtype": line[2],
                  "x": x,
                  "y": y,
                  "r": r,
                  "padx": padx,
                  "pady": pady,
                  "drill": drill
                }

            else:
              print("ERORR: While parsing PCB file, found UNKNOWN PAD TYPE!")
              sys.exit(1)

            pads.append(new_pad)

          # New footprint definition denotes end of current footprint components, 
          # thus we move onto the next component on the list of footprints
          elif ("(footprint " in line):
            break

# Collects segment data for traces in the pcb file,
# as well as via data to connect traces, 
# along with the PCB outline data. 
# Data for Traces & Vias are returned on the 'segs' list,
# and data for the board outline is returned on the 'outlines' list.
# TODO: Note that this only supports 2 layer boards at this time.
# TODO: Currently assumes all trace widths are all the same. 
    # Trace Data
        #   "type": "segment",
        #   "x0": x0,
        #   "y0": y0,
        #   "x1": x1,
        #   "y1": y1, 
        #   "width": width,
        #   "layer": layer,
        #   "net": net #
    # Via Data 
        #   "type": "via",
        #   "x": x,
        #   "y": y,
        #   "size": size,
        #   "drill": drill,
        #   "net": net
def assign_segments(file: str, segs: list, outlines: list):
  with open(file, 'r') as pcbfile:
    line = pcbfile.readline()
    outline = (0, 0, 0, 0)
    while line:
      # Collecting Segments
      if ("(segment" in line):
        # Start and end x, y
        startline = pcbfile.readline()
        endline = pcbfile.readline()
        startline = (startline.strip())[1:-1]
        endline = (endline.strip())[1:-1]
        startline = startline.split()
        endline = endline.split()
        x0 = startline[1]
        y0 = startline[2]
        x1 = endline[1]
        y1 = endline[2]

        # Width 
        widthline = pcbfile.readline()
        widthline = (widthline.strip())[1:-1]
        widthline = widthline.split()
        width = widthline[1]

        # Layer
        layerline = pcbfile.readline()
        layerline = (layerline.strip())[1:-1]
        layerline = layerline.split()
        layer = layerline[1][1:-1]

        # Net
        netline = pcbfile.readline()
        netline = (netline.strip())[1:-1]
        netline = netline.split()
        net = "net_" + netline[1]

        new_seg = {
          "type": "segment",
          "x0": x0,
          "y0": y0,
          "x1": x1,
          "y1": y1, 
          "width": width,
          "layer": layer,
          "net": net
        }

        segs.append(new_seg)

      # Collecting Vias
      elif ("(via" in line) and not("(vias" in line):
        locline = (pcbfile.readline().strip())[1:-1]
        sizeline = (pcbfile.readline().strip())[1:-1]
        drillline = (pcbfile.readline().strip())[1:-1]
        pcbfile.readline()
        net = "net_" + (((pcbfile.readline().strip())[1:-1]).split())[1]

        locline = locline.split()
        x = locline[1]
        y = locline[2]

        sizeline = sizeline.split()
        size = sizeline[1]
        drillline = drillline.split()
        drill = drillline[1]
        
        new_via = {
          "type": "via",
          "x": x,
          "y": y,
          "size": size,
          "drill": drill,
          "net": net
        }

        segs.append(new_via)

        # TODO: Add code to make it compatible with 2+ layer boards
        # This assumes only F.Cu and B.Cu layers!
      
      elif ("(gr" in line):
        line = line.strip()
        if (line == "(gr_rect"):
          startline = pcbfile.readline()
          endline = pcbfile.readline()

          startline = (startline.strip())[1:-1]
          endline = (endline.strip())[1:-1]
          startline = startline.split()
          endline = endline.split()

          x0 = startline[1]
          y0 = startline[2]
          x1 = endline[1]
          y1 = endline[2]

          outline = ('rect', x0, y0, x1, y1)
          outlines.append(outline)
        elif (line == "(gr_line"):
          startline = pcbfile.readline()
          endline = pcbfile.readline()

          startline = (startline.strip())[1:-1]
          endline = (endline.strip())[1:-1]
          startline = startline.split()
          endline = endline.split()

          x0 = startline[1]
          y0 = startline[2]
          x1 = endline[1]
          y1 = endline[2]

          outline = ('line', x0, y0, x1, y1)
          outlines.append(outline)
        elif (line == "(gr_arc"):
          startpt = pcbfile.readline()
          midpt = pcbfile.readline()
          endpt = pcbfile.readline()

          startpt = (startpt.strip())[1:-1]
          midpt = (midpt.strip())[1:-1]
          endpt = (endpt.strip())[1:-1]
          startpt = startpt.split()
          midpt = midpt.split()
          endpt = endpt.split()

          x0 = startpt[1]
          y0 = startpt[2]
          x1 = midpt[1]
          y1 = midpt[2]
          x2 = endpt[1]
          y2 = endpt[2]

          outline = ('arc', x0, y0, x1, y1, x2, y2)
          outlines.append(outline)
        
      line = pcbfile.readline()
  
# Grabs the PCB File from filesystem. 
def get_pcb_file():
    filename, filter = PySide2.QtWidgets.QFileDialog.getOpenFileName(filter="KiCad printed citcuit board files (*kicad_pcb)")
    return filename

# Helper Function to draw_traces(),
# Inserts 'joints' in the form of cylinders between
# Trace 'blocks' to fill in the gaps so that trace segments 
# Form one trace line without breaks and gaps
def create_joint(name, x0, y0, x1, y1, wid, layer):
  jointA = name + "A"
  jointB = name + "B"
  obj_cilA = DOC.addObject("PartDesign::AdditiveCylinder", jointA)
  obj_cilA.Radius = wid/2
  obj_cilA.Height = wid

  obj_cilB = DOC.addObject("PartDesign::AdditiveCylinder", jointB)
  obj_cilB.Radius = wid/2
  obj_cilB.Height = wid

  if (layer == "F.Cu"):
    cir_locationA = FreeCAD.Vector(float(x0), float(y0), DEFAULT_FCU_Z)
    cir_locationB = FreeCAD.Vector(float(x1), float(y1), DEFAULT_FCU_Z)
  else:
    cir_locationA = FreeCAD.Vector(float(x0), float(y0), DEFAULT_BCU_Z)
    cir_locationB = FreeCAD.Vector(float(x1), float(y1), DEFAULT_BCU_Z)

  obj_cilA.Placement.Base = cir_locationA
  obj_cilB.Placement.Base = cir_locationB

# Helper Function to draw_traces(),
# Creates Traces in the form of long rectangular boxes. 
def create_trace(name, len, wid, hei, x0, y0, layer, orientation):
    obj_box = DOC.addObject("PartDesign::AdditiveBox", name)
    obj_box.Length = len
    obj_box.Width = wid
    obj_box.Height = hei

    # Rotate the created trace here...
    match orientation:
      case "N":
        rot = Rotation(90, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) + (wid/2), float(y0), DEFAULT_FCU_Z)   
        else:
          location = FreeCAD.Vector(float(x0) + (wid/2), float(y0), DEFAULT_BCU_Z)
      case "S":
        rot = Rotation(-90, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) - (wid/2), float(y0), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0) - (wid/2), float(y0), DEFAULT_BCU_Z)
      case "E":
        rot = Rotation(0, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0), float(y0) - (wid/2), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0), float(y0) - (wid/2), DEFAULT_BCU_Z)
      case "W":
        rot = Rotation(180, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0), float(y0) + (wid/2), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0), float(y0) + (wid/2), DEFAULT_BCU_Z)
      case "NE":
        rot = Rotation(45, 0, 0) 
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) + ((wid/2) / math.sqrt(2)), float(y0) - ((wid/2) / math.sqrt(2)), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0) + ((wid/2) / math.sqrt(2)), float(y0) - ((wid/2) / math.sqrt(2)), DEFAULT_BCU_Z)
      case "NW":
        rot = Rotation(135, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) + ((wid/2) / math.sqrt(2)), float(y0) + ((wid/2) / math.sqrt(2)), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0) + ((wid/2) / math.sqrt(2)), float(y0) + ((wid/2) / math.sqrt(2)), DEFAULT_BCU_Z)
      case "SW":
        rot = Rotation(225, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) - ((wid/2) / math.sqrt(2)), float(y0) + ((wid/2) / math.sqrt(2)), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0) - ((wid/2) / math.sqrt(2)), float(y0) + ((wid/2) / math.sqrt(2)), DEFAULT_BCU_Z)
      case "SE":
        rot = Rotation(315, 0, 0)
        if (layer == "F.Cu"):
          location = FreeCAD.Vector(float(x0) - ((wid/2) / math.sqrt(2)), float(y0) - ((wid/2) / math.sqrt(2)), DEFAULT_FCU_Z)
        else:
          location = FreeCAD.Vector(float(x0) - ((wid/2) / math.sqrt(2)), float(y0) - ((wid/2) / math.sqrt(2)), DEFAULT_BCU_Z)

    obj_box.Placement.Base = location
    obj_box.Placement.Rotation = rot

    return obj_box

# Helper Function to draw_traces()
# TODO: This only supports double layer boards,
# where it assumes there is only F and B layers 
# when connecting the traces with a via
def create_via(name, x, y, size):
  obj_via = DOC.addObject("Part::Cylinder", name)
  obj_via.Radius = float(size)/2
  obj_via.Height = abs(DEFAULT_FCU_Z) + abs(DEFAULT_BCU_Z) + DEFAULT_TRACE_HEIGHT

  cir_location = FreeCAD.Vector(float(x), float(y), DEFAULT_FCU_Z)
  obj_via.Placement.Base = cir_location

# Function to implement anything trace related
# Calls functions to draw trace segments, trace joints, and vias
def draw_traces(segs: list, ftpt: list):
  cnt = 1
  trace_names = list()
  for item in segs:
    if (item["type"] == "segment"):
      trace_name = "trace_seg" + str(cnt)
      joint_name = "joint_seg" + str(cnt)

      x0 = float(item["x0"])
      x1 = float(item["x1"])
      y0 = float(item["y0"])
      y1 = float(item["y1"])

      x = (x1 - x0) ** 2
      y = (y1 - y0) ** 2
      len = round(math.sqrt(x + y), 4)
      
      # Need to figure out orientation of the trace! 
      # Fortunately, orientation is limited to N,S,E,W, and the 45's
      if (x0 == x1): # Vertical, N or S
        if (y0 < y1):
          orientation = 'N'
        else:
          orientation = 'S'
      elif (y0 == y1): # Horizontal, E or W
        if (x0 < x1):
          orientation = 'E'
        else:
          orientation = 'W'
      elif (x0 < x1) and (y0 < y1):
        orientation = 'NE'
      elif (x0 < x1) and (y0 > y1):
        orientation = 'SE'
      elif (x0 > x1) and (y0 < y1):
        orientation = 'NW'
      else:
        orientation = "SW"

      # print("Ort:", orientation)

      # Make sure this does not exclude valid trace segments!
      if (len < MINIMUM_TRACE_LENGTH):
        print("   Trace len:", len, " is too short, skipping")
        
      # elif (item["layer"] == "B.Cu"):
      else:
        # create_trace(trace_name, len, float(item["width"]), float(item["width"]), x0, y0, item["layer"], orientation)
        # create_joint(joint_name, x0, y0, x1, y1, float(item["width"]), item["layer"])

        # Currently using global values as trace width & height
        create_trace(trace_name, len, DEFAULT_TRACE_WIDTH, DEFAULT_TRACE_HEIGHT, x0, y0, item["layer"], orientation)
        create_joint(joint_name, x0, y0, x1, y1, DEFAULT_TRACE_WIDTH, item["layer"])

        # Combines each trace segment with their 2 joints on each end into 
        # one PartDesign body to speed up boolean operation
        bodyname = trace_name + "_body"
        DOC.addObject("PartDesign::Body", bodyname)
        DOC.getObject(bodyname).addObject(DOC.getObject(trace_name))
        DOC.getObject(bodyname).addObject(DOC.getObject(str(joint_name + "A")))
        DOC.getObject(bodyname).addObject(DOC.getObject(str(joint_name + "B")))
        DOC.recompute()
        trace_names.append(bodyname)

    elif (item["type"] == "via"): 
      via_name = "via_net_" + str(cnt)
      trace_names.append(via_name)
      create_via(via_name, item["x"], item["y"], item["size"])

    cnt = cnt + 1
    if (cnt % REFRESH_RATE == 0) and (MOVIE_EFFECT):
      set_view()
  return trace_names

# Helper function to draw_pads(), 
# Draws the pads for SMD components
def draw_smd_pad(name: str, item, x: float, y: float, r: float, layer: str):
  if (layer == "F.Cu"):
    pad_loc = FreeCAD.Vector(x, y, DEFAULT_FCU_Z - DEFAULT_PAD_HEIGHT)
  else: 
    pad_loc = FreeCAD.Vector(x, y, DEFAULT_BCU_Z + DEFAULT_TRACE_HEIGHT)
  pad_rot = Rotation(int(item["r"]), 0, 0)

  # TODO: All SMD Pads have been roundrect or rect so far... 
  if (item["padtype"] == "roundrect") or (item["padtype"] == "rect"):
    obj_pad = DOC.addObject("Part::Box", name)

    # obj_pad.Length = float(item["padx"])
    # obj_pad.Width = float(item["pady"])
    # Using trace width x height, instead of pad dimension data
    obj_pad.Length = DEFAULT_TRACE_WIDTH * 1.05
    obj_pad.Width = DEFAULT_TRACE_HEIGHT * 1.05
    
    obj_pad.Height = DEFAULT_PAD_HEIGHT
  else:
    print("Unsupported SMD Pad Shape: ", item["padtype"])
    sys.exit(1)

  obj_pad.Placement.Base = pad_loc
  obj_pad.Placement.Rotation = pad_rot

# Helper function to draw_pads(), 
# Draws the pads for through hole components
def draw_thru_hole_pad(name: str, item, plx: float, ply: float, r: float, layer: str):
  
  pad_rot = Rotation(int(item["r"]), 0, 0)

  # Both throughhole types make a circular hole, 
  # regardless of the Pad shape. 
  if (item["padtype"] == "oval") or (item["padtype"] == "circle"):
    obj_pad = DOC.addObject("Part::Cylinder", name)
    obj_pad.Radius = float(item["drill"])/2 * (1.2) # 20% oversize to account for 3D printing & fitting

    if (layer == "F.Cu"):
      pad_loc = FreeCAD.Vector(plx, ply, DEFAULT_BCU_Z + DEFAULT_TRACE_HEIGHT)
      obj_pad.Height = DEFAULT_THRUHOLE_HEIGHT
      pad_rot = Rotation(0, 0, 180)
    else:
      pad_loc = FreeCAD.Vector(plx, ply, DEFAULT_FCU_Z)
      obj_pad.Height = DEFAULT_THRUHOLE_HEIGHT
    
  elif (item["padtype"] == "rect"):
    obj_pad = DOC.addObject("Part::Cylinder", name)
    obj_pad.Radius = float(item["drill"])/2 * (1.2) # 20% oversize to account for 3D printing & fitting

    if (layer == "F.Cu"):
      pad_loc = FreeCAD.Vector(plx, ply, DEFAULT_BCU_Z + DEFAULT_TRACE_HEIGHT)
      obj_pad.Height = DEFAULT_THRUHOLE_HEIGHT
      pad_rot = Rotation(0, 0, 180)
    else:
      pad_loc = FreeCAD.Vector(plx, ply, DEFAULT_FCU_Z)
      obj_pad.Height = DEFAULT_THRUHOLE_HEIGHT

  else:
    print("Unsupported Thru_Hole Pad Shape: ", item["padtype"])
    sys.exit(1)

  obj_pad.Placement.Base = pad_loc
  obj_pad.Placement.Rotation = pad_rot

# Draws the pads of each component
# Currently Pad dimensions are set to the global trace height x width
def draw_pads(pads: list):
  cnt = 1
  pad_names = list()
  for item in pads:
    footpt = item["footprint"]
    # xdim = float(item["padx"])
    # ydim = float(item["pady"])
    xdim = DEFAULT_TRACE_WIDTH
    ydim = DEFAULT_TRACE_HEIGHT
    
    ##################################################    
    # Pad orientation adjustments for top side pads
    ##################################################    
    if (footpt["layer"] == "F.Cu"): 
      if (int(item["r"]) == 90):
        plx = float(footpt["x"]) + float(item["y"])
        ply = float(footpt["y"]) - float(item["x"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx + ydim/2
          ply = ply - xdim/2
      elif (int(item["r"]) == 270) or (int(item["r"]) == -90):
        plx = float(footpt["x"]) - float(item["y"])
        ply = float(footpt["y"]) + float(item["x"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx - ydim/2
          ply = ply + xdim/2
      elif (int(item["r"]) == 0):
        plx = float(footpt["x"]) + float(item["x"])
        ply = float(footpt["y"]) + float(item["y"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx - xdim/2
          ply = ply - ydim/2
      elif (int(item["r"]) == 180):
        plx = float(footpt["x"]) - float(item["x"])
        ply = float(footpt["y"]) - float(item["y"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx + xdim/2
          ply = ply + ydim/2
    ##################################################     
    # Pad orientation adjustments for bottom side pads
    ##################################################    
    elif (footpt["layer"] == "B.Cu"):
      if (int(item["r"]) == 90):
        plx = float(footpt["x"]) + float(item["y"])
        ply = float(footpt["y"]) - float(item["x"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx + ydim/2
          ply = ply - xdim/2
      elif (int(item["r"]) == 270) or (int(item["r"]) == -90):
        plx = float(footpt["x"]) - float(item["y"])
        ply = float(footpt["y"]) + float(item["x"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx - ydim/2
          ply = ply + xdim/2
      elif (int(item["r"]) == 0):
        plx = float(footpt["x"]) + float(item["x"])
        ply = float(footpt["y"]) + float(item["y"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx - xdim/2
          ply = ply - ydim/2
      elif (int(item["r"]) == 180):
        plx = float(footpt["x"]) - float(item["x"])
        ply = float(footpt["y"]) - float(item["y"])
        if (item["type"] == "smd") and (item["padtype"] != "circle") and (item["padtype"] != "oval"):
          plx = plx + xdim/2
          ply = ply + ydim/2

    if (item["type"] == "smd"):
      pad_names.append(item["name"] + "_smdpad_" + str(cnt))
      draw_smd_pad(item["name"] + "_smdpad_" + str(cnt), item, plx, ply, float(footpt["r"]), footpt["layer"])
    elif (item["type"] == "thru_hole"):
      pad_names.append(item["name"] + "_thrupad_" + str(cnt))
      draw_thru_hole_pad(item["name"] + "_thrupad_" + str(cnt), item, plx, ply, float(footpt["r"]), footpt["layer"])
    
    cnt = cnt + 1
    # if (cnt % REFRESH_RATE == 0) and (MOVIE_EFFECT):
    #   set_view()
  return pad_names  

# Will create the overall body to enclose the traces and pads created
def create_body(outlines: list): 
  outline_segs = list()
  for line in outlines:
    # This assumes that if you have a 'rect' shape in your board outline, 
    # that 'rect' completes the board shape. 
    # Otherwise, it is composed of lines and arcs
    if (line[0] == "rect"): 
      x0 = float(line[1])
      y0 = float(line[2])
      x1 = float(line[3])
      y1 = float(line[4])

      V1 = App.Vector(x0, y0, DEFAULT_BODY_FCU_Z)
      V2 = App.Vector(x0, y1, DEFAULT_BODY_FCU_Z)
      V3 = App.Vector(x1, y0, DEFAULT_BODY_FCU_Z)
      V4 = App.Vector(x1, y1, DEFAULT_BODY_FCU_Z)

      L1 = Part.LineSegment(V1, V2)
      L2 = Part.LineSegment(V1, V3)
      L3 = Part.LineSegment(V2, V4)
      L4 = Part.LineSegment(V3, V4)

      S1 = Part.Shape([L1, L2, L3, L4])
      W = Part.Wire(S1.Edges)
      face = Part.Face(W)
      board_shape = face.extrude(App.Vector(0, 0, DEFAULT_BODY_HEIGHT))
      Part.show(board_shape)
      DOC.addObject("PartDesign::Body", "PCB_Base")
      DOC.getObject('PCB_Base').Label = 'PCB_Base'
      DOC.PCB_Base.BaseFeature = DOC.Shape

      DOC.getObject("PCB_Base").Visibility = False
      DOC.getObject("Shape").Visibility = False
      if (MOVIE_EFFECT):
        set_view()
      return board_shape
    # If the board is non-retangular, it must go through this 
    # seemingly convoluted process in order to create a viable solid.
    # Thus, the sorting of line segments is needed as seen in 
    # the function sort_outlines()
    elif (line[0] == "line"):
      x0 = float(line[1])
      y0 = float(line[2])
      x1 = float(line[3])
      y1 = float(line[4])

      V1 = App.Vector(x0, y0, DEFAULT_BODY_FCU_Z)
      V2 = App.Vector(x1, y1, DEFAULT_BODY_FCU_Z)

      L1 = Part.LineSegment(V1, V2)
      outline_segs.append(L1)
      # print("Line Created:", L1)
    elif (line[0] == "arc"):
      x0 = float(line[1])
      y0 = float(line[2])
      x1 = float(line[3])
      y1 = float(line[4])
      x2 = float(line[5])
      y2 = float(line[6])

      V1 = App.Vector(x0, y0, DEFAULT_BODY_FCU_Z)
      V2 = App.Vector(x1, y1, DEFAULT_BODY_FCU_Z)
      V3 = App.Vector(x2, y2, DEFAULT_BODY_FCU_Z)

      A1 = Part.Arc(V1, V2, V3)
      outline_segs.append(A1)
      # print("Arc Created:", A1)
    else:
      print("Unsupported Outline Option!")
      sys.exit(1)
  
  S1 = Part.Shape(outline_segs)
  W = Part.Wire(S1.Edges)
  face = Part.Face(W)
  board_shape = face.extrude(App.Vector(0, 0, DEFAULT_BODY_HEIGHT))
  Part.show(board_shape)

  DOC.addObject("PartDesign::Body", "PCB_Base")
  DOC.getObject('PCB_Base').Label = 'PCB_Base'
  DOC.PCB_Base.BaseFeature = DOC.Shape

  # DOC.getObject("PCB_Base").Visibility = False
  DOC.getObject("Shape").Visibility = False

  if (MOVIE_EFFECT):
        set_view()
  return board_shape   

# This function pulls 3d .step file names from the PCB file. 
# Then, it goes to the user-determined KiCAD 3dmodels directory 
# (See Global Variable "KICAD_3DMODEL_DIR", see README for further details)
# to grab and insert the actual model for each component. 
# These models are the 'socket' designs used in the DissolvPCB process. 
# The imported .step files are rotated and placed accordingly.
def insert_package_models(file: str, ftpt: list, step_files: list):
  with open(file, 'r') as pcbfile:
   
    for footprint in ftpt:
      pcbfile.seek(footprint["filepos"])
      line = pcbfile.readline()
      line = pcbfile.readline()
      cnt = 1
      while not (("(footprint" in line) or ("(gr_rect" in line) or ("(gr_line" in line) or ("(segment" in line)):
        line = pcbfile.readline()
        
        if ("(model" in line):
          # print("reading model")
          step_file_line = (line.strip())[8:-1]
          # print("Step File: ", step_file_line)

          k = step_file_line.find("3DMODEL_DIR}")
          step_file_dir = KICAD_3DMODEL_DIR + str(step_file_line[k + 13:])
          # print("Step File Dir: ", step_file_dir)

          i = step_file_line.rfind("/")
          step_file_name = step_file_line[i+1:-5]
          # print("Stepfile Name: ", step_file_name)

          pcbfile.readline()
          offset_line = pcbfile.readline()
          pcbfile.readline()
          pcbfile.readline()
          scale_line = pcbfile.readline()
          pcbfile.readline()
          pcbfile.readline()
          rot_line = pcbfile.readline()

          offset_line = ((offset_line.strip())[4:-1]).split()
          scale_line = ((scale_line.strip())[4:-1]).split()
          rot_line = ((rot_line.strip())[4:-1]).split()

          model = ImportGui.insert(step_file_dir, DOC_NAME, useLinkGroup = True)
          new_name = "housing_" + footprint["name"] + "_" + str(cnt)
          model.Label = new_name

          x = footprint["x"] + float(offset_line[0])
          y = footprint["y"] + float(offset_line[1])

          # F.Cu Layer Components
          if (footprint["layer"] == "F.Cu"):
            if (footprint ["r"] == 90): 
              x = footprint["x"] + float(offset_line[1])
              y = footprint["y"] - float(offset_line[0])
            elif (footprint ["r"] == 270) or (footprint ["r"] == -90): 
              x = footprint["x"] - float(offset_line[1])
              y = footprint["y"] + float(offset_line[0])
            elif (footprint ["r"] == 0): 
              x = footprint["x"] + float(offset_line[0])
              y = footprint["y"] + float(offset_line[1])
            elif (footprint ["r"] == 0): 
              x = footprint["x"] - float(offset_line[0])
              y = footprint["y"] - float(offset_line[1])

            z = DEFAULT_BODY_FCU_Z + DEFAULT_SOCKET_HEIGHT - float(offset_line[2])

            rot_x = (-1 * int(footprint["r"])) + int(rot_line[2])
            rot_y = 0 
            rot_z = 180 

          # B.Cu Layer Components
          else:
            z = DEFAULT_BODY_BCU_Z - DEFAULT_SOCKET_HEIGHT + float(offset_line[2]) 
            rot_x = int(rot_line[2]) + int(footprint["r"])
            rot_y = 0
            rot_z = 0

            if (rot_x == 90):
              rot_x = -90
            elif (rot_x == 270) or (rot_x == -90):
              rot_x = 90

          footprint_loc = FreeCAD.Vector(x, y, z)
          footprint_rot = Rotation(rot_x, rot_y, rot_z)
          # print("Placement", x, ", ", y, ", ", z)
          # print("Rotation", rot_x, ", ", rot_y, ", ", rot_z, "\n\n")

          model.Placement.Base = footprint_loc
          model.Placement.Rotation = footprint_rot
          
          step_files.append(new_name)
          cnt = cnt + 1

# Creating body when the list of segments do not have any matching 
# Coordinates fails to connect the segment to the rest of the edges, 
# resulting in a incomplete shape.
# This function returns a list of sorted outline segments to guarentee
# that each subsequent segment pair has at least one matching coordinate
def sort_outlines(outlines: list): 
  newlist = list()
  newlist.append(outlines[0])

  if (len(outlines) <= 1):
    return outlines
  else: 
    for i in range(1, len(outlines)):
      # print("iteration: ", i)
      curr = outlines[i]
      x0 = curr[1]
      y0 = curr[2]
      if (curr[0] == 'arc'):
        xEnd = curr[5]
        yEnd = curr[6]
      else:
        xEnd = curr[3]
        yEnd = curr[4]
      
      curr_start = (x0, y0)
      curr_end = (xEnd, yEnd)

      for prev in newlist:
        x0 = curr[1]
        y0 = curr[2]
        if (prev[0] == 'arc'):
          xEnd = prev[5]
          yEnd = prev[6]
        else:
          xEnd = prev[3]
          yEnd = prev[4]
        prev_start = (x0, y0)
        prev_end = (xEnd, yEnd)
        
        if (curr_start == prev_start) or (curr_start == prev_end) or (curr_end == prev_start) or (curr_end == prev_end):
          # print("found matching ends")
          pos = newlist.index(prev)
          newlist.insert(pos + 1, curr)
          break

  return newlist

# Takes in a list of ojects (composed of traces, pads, vias, etc.)
# and adds them to the 'boolean property' of the main Body.
# Does 2 boolean operations, 1 cut operation (see "Cut_Bool") for 
# Cutting out traces, vias, and pads, and 1 fuse operation (see "Fuse_Bool")
# for fusing socket models. 
# IMPORTANT: 
  # DOC.recompute() must be called to actually
  # perform the boolean operation. Takes 1 hr+ if recompute is 
  # called for each component instead of calling it once at the end...
# TODO: Explore optimization of the boolean step
def do_boolean_op(objects: list, step_files: list):
  # Cut Objects & Loop
  DOC.getObject("PCB_Base").newObject("PartDesign::Boolean", "Cut_Bool")
  DOC.getObject('Cut_Bool').Type = 1
  DOC.recompute()
  
  DOC.getObject("PCB_Base").Tip = DOC.getObject("BaseFeature")
  for obj in objects:
    # print("Obj:", obj)
    DOC.getObject('Cut_Bool').addObjects([DOC.getObject(str(obj))])
  DOC.recompute()

  # Fuse Objects & Loop
  DOC.getObject("PCB_Base").newObject("PartDesign::Boolean", "Fuse_Bool")
  DOC.getObject('Fuse_Bool').Type = 0
  DOC.recompute()

  DOC.getObject("PCB_Base").Tip = DOC.getObject("Cut_Bool")
  for name in step_files:
    # print("Obj:", name)
    DOC.getObject('Fuse_Bool').addObjects([DOC.getObjectsByLabel(name)[0]])
  DOC.recompute() 
   
def main():
  print('Welcome to PVA-LM PCB Project!')

  filename = get_pcb_file()

  ftpt = list()
  pads = list()
  segs = list()
  outlines = list() 
  objects = list()
  step_files = list()

#####################################################
#////////////PCB File Parsing Steps//////////////////#
#####################################################
  # 
  # Collect All footprint-related data from PCB File
  assign_footprints(filename, ftpt)

  # Collect All pads by each component
  assign_pads(filename, ftpt, pads)

  # Collect All Segments (and Vias) + board outline data
  assign_segments(filename, segs, outlines)

  print("PCB File Parsing Successful!")

#####################################################
#//////////////PCB Generation Steps/////////////////#
#####################################################

  #####################################################
  # Trace and Pad Generation
  #####################################################
  trace_objs = draw_traces(segs, ftpt)
  pad_objs = draw_pads(pads)
  objects = trace_objs + pad_objs
  DOC.recompute()
  
  #####################################################
  # DissolvPCB Body Generation
  #####################################################
  outlines = sort_outlines(outlines)
  create_body(outlines)
  DOC.recompute()

  #####################################################
  # 3D Footprint Insertion
  #####################################################
  insert_package_models(filename, ftpt, step_files)
  DOC.recompute()

  #####################################################
  # Boolean Operation
  #####################################################
  do_boolean_op(objects, step_files)
  DOC.recompute()
  DOC.getObject("PCB_Base").Visibility = True
  DOC.getObject("Cut_Bool").Visibility = True

  set_view()

  print("PCB Generation Complete!")

  ftpt.clear()
  pads.clear()
  segs.clear()
  outlines.clear()
  objects.clear()
  step_files.clear()

if __name__ == "__main__":
  main()
