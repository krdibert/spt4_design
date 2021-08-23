#This file contains all components used in my SPT4 masks.
#All default variables here should be overridden in settings.py
#To override a hardcoded variable, just make it an argument of the function, and add that argument as a key in the appropriate settings.py dictionary.

import gdspy
from math import pi, sin, asin, cos, acos, radians
import phidl
from phidl import geometry as geo
from phidl import path as pp
import numpy as np


def polypath_from_points(xypoints = [(0,0), (1,0), (1,1)], lw = None, name = None, inc_ports = True, layer = 0, **pathkwargs ):
    """Helper function to create a set of polygons that follow a path defined by xypoints.

    xypoints = [(x0,y0), (x1,y1)... (xn,yn)]

    """

    name = "polypath" if not name else str(name)
    polypath = phidl.Device(name=name)

    if isinstance(xypoints, gdspy.FlexPath): #and not lw:
        print( "got flexpath and no lw - using path defined lw")
        # use the lw defined in the FlexPath
        polypath.add_polygon( xypoints.get_polygons(), layer = layer )
        lwin, lwout = xypoints.widths.flatten()[[0,-1]]
        xypoints = xypoints.points

    # elif isinstance(xypoints, gdspy.FlexPath) and isinstance(lw, (int, float, np.float) ):
    #     print "got flexpath and new lw - redefining path"
    #     # create a new path with the given linewidth
    #     polypath.add_polygon( gdspy.FlexPath(xypoints.points, lw, **pathkwargs).get_polygons(), layer = layer)
    #     xypoints = xypoints.points

    else:
        xypoints = np.array(xypoints)
        polypath.add_polygon( gdspy.FlexPath(xypoints, lw, **pathkwargs).get_polygons(), layer = layer)
        lwin = lwout = lw
    # add ports
    if inc_ports == True:
        # calulate angles for the first and last segments
        z = np.array(xypoints.T)[0] + 1j*np.array(xypoints.T)[1]
        segangles = np.rad2deg( np.angle( np.diff(z) ) ) #+ 180.

        polypath.add_port( name = name+"1", midpoint = xypoints[0], width = lwin, orientation  = segangles[0]+180 ) # flip orientation of input port
        polypath.add_port( name = name+"2", midpoint = xypoints[-1], width = lwout, orientation = segangles[-1] )

    return polypath

def arc_idc(start_angle=0, theta=180, outer_radius=1000, tine_spacing=5, tine_linewidth=5, numtines=10, rail_width=10,
        rail_extend_in = 0, rail_extend_out = 0,
        layer = 0, **kwargs):

    idc = phidl.Device(name = "idc")

    tines = phidl.Device(name = "idc_tines")

    cap_width = numtines*(tine_linewidth + tine_spacing) - tine_spacing
    inner_radius = outer_radius - cap_width
    

    for i in range(numtines):

        radius = outer_radius - i * (tine_spacing + tine_linewidth)
        end_gap_angle = 180 * tine_spacing /(pi * radius)

        if i%2==0: tine = geo.arc(radius=radius, width = tine_linewidth, theta = theta - end_gap_angle, start_angle = start_angle, angle_resolution = 1, layer = layer)
        else: tine = geo.arc(radius=radius, width = tine_linewidth, theta = theta - end_gap_angle, start_angle = start_angle + end_gap_angle, angle_resolution = 1, layer = layer)

        tine_ref = tines.add_ref(tine)


    # create the rails
    rail_extend_bottom = rail_extend_out
    rail_extend_top = rail_extend_in

    rails = geo.Device(name="idc_rails")
    rail_height = cap_width + rail_extend_in + rail_extend_out
    rail_radius = outer_radius + rail_extend_out

    x_offset_0 = cos(radians(start_angle)) * rail_radius + sin(radians(start_angle)) * rail_width
    y_offset_0 = sin(radians(start_angle)) * rail_radius - cos(radians(start_angle)) * rail_width
    x_offset_1 = cos(radians(start_angle + theta)) * rail_radius  #- sin(radians(start_angle))# * tine_spacing
    y_offset_1 = sin(radians(start_angle + theta)) * rail_radius #+ cos(radians(start_angle)) #* tine_spacing

    rails.add_ref( geo.rectangle((-rail_height, rail_width ), layer = layer) ).rotate(start_angle).movex(x_offset_0).movey(y_offset_0)
    rails.add_ref( geo.rectangle((-rail_height, rail_width ), layer = layer) ).rotate(start_angle+theta).movex(x_offset_1).movey(y_offset_1)
                                                                            
    idc.add_ref((tines, rails))

    # add ports
    out_port_radius = rail_radius
    in_port_radius = outer_radius - rail_extend_in - cap_width

    x_port_1 = cos(radians(start_angle)) * out_port_radius + sin(radians(start_angle)) * rail_width/2.
    y_port_1 = sin(radians(start_angle)) * out_port_radius - cos(radians(start_angle)) * rail_width/2.
    x_port_2 = cos(radians(start_angle)) * in_port_radius + sin(radians(start_angle)) * rail_width/2.
    y_port_2 = sin(radians(start_angle)) * in_port_radius - cos(radians(start_angle)) * rail_width/2.
    x_port_3 = cos(radians(start_angle + theta)) * out_port_radius - sin(radians(start_angle + theta)) * rail_width/2.
    y_port_3 = sin(radians(start_angle + theta)) * out_port_radius + cos(radians(start_angle + theta)) * rail_width/2.
    x_port_4 = cos(radians(start_angle + theta)) * in_port_radius  - sin(radians(start_angle + theta)) * rail_width/2.
    y_port_4 = sin(radians(start_angle + theta)) * in_port_radius + cos(radians(start_angle + theta)) * rail_width/2.

    idc.add_port( name = "idc_1", midpoint = (x_port_1, y_port_1), orientation = start_angle )
    idc.add_port( name = "idc_2", midpoint = (x_port_2, y_port_2), orientation = start_angle + 180. )
    idc.add_port( name = "idc_3", midpoint = (x_port_3, y_port_3), orientation = start_angle + theta )
    idc.add_port( name = "idc_4", midpoint = (x_port_4, y_port_4), orientation = start_angle + theta + 180 )

    return idc

def rect_idc(tine_length = 1000, tine_spacing=5, tine_linewidth=5, numtines=10, rail_width=10,
        rail_extend_top = 0, rail_extend_bottom = 0,
        sep = 0.,
        layer_1 = None, layer_2=None, **kwargs):

    width=tine_length

    idc = phidl.Device(name = "idc")
    # create rectangles for capacitor tines (origin is lower left corner)
    tine_1 = geo.rectangle((width, tine_linewidth), layer = layer_1)
    tine_2 = geo.rectangle((width, tine_linewidth), layer = layer_2)

    tines = phidl.Device(name = "idc_tines")
    refs=[]
    for i in range(numtines):
        if i%2==1: refs.append(tines.add_ref(tine_1).movey(i * (tine_linewidth+tine_spacing) ))
        else: refs.append(tines.add_ref(tine_2).movey(i * (tine_linewidth+tine_spacing) ))
    [x.movex(destination=tine_spacing + sep) for x in refs[::2]]

    # create the rails
    rails = geo.Device(name="idc_rails")
    rail_height = numtines*(tine_linewidth + tine_spacing) + rail_extend_top + rail_extend_bottom
    rails.add_ref( geo.rectangle((-rail_width, rail_height ), layer = layer_1) ).movey(-rail_extend_bottom)
    rails.add_ref( geo.rectangle((-rail_width, rail_height ), layer = layer_2).movey(-rail_extend_bottom)\
                                                                            .movex(width + tine_spacing + rail_width + sep) )
    idc.add_ref((tines, rails))

    # add ports
    idc.add_port( name = "idc_1", midpoint = (-rail_width/2., -rail_extend_bottom), orientation = -90. )
    idc.add_port( name = "idc_2", midpoint = (-rail_width/2., rail_height-rail_extend_bottom), orientation = 90. )
    idc.add_port( name = "idc_3", midpoint = (width+ tine_spacing + rail_width/2. , -rail_extend_bottom), orientation = -90. )
    idc.add_port( name = "idc_4", midpoint = (width+ tine_spacing + rail_width/2., rail_height-rail_extend_bottom), orientation = 90. )

    return idc

#--------------------------------------------------------------------------------


#utility function for making a segment of an absorber
def absorber_segment(lw, start_length, function, num_unit, center_spacing, layer):

    points=[]
    offset = lw/2.
    shift = center_spacing/2.
    start = [0, offset]
    points.append(start)

    for u in range(num_unit):
        length = function(u, start_length)
        point_1 = [offset-length - shift, offset + 4*lw*u]
        point_2 = [offset-length - shift, 2*lw+offset + 4*lw*u]
        point_3 = [-offset - shift, 2*lw+offset + 4*lw*u]
        point_4 = [-offset - shift, 4*lw+offset + 4*lw*u]
        points.append(point_1)
        points.append(point_2)
        if u < num_unit-1:
            points.append(point_3)
            points.append(point_4)

    point_extend = [ offset - length - shift, 2*lw+offset + 4*lw*num_unit]
    points.append(point_extend)

    br = lw
    if start_length==4: corners='smooth'
    else: corners = 'circular bend'
    segment=polypath_from_points(xypoints = points, lw = lw, name = None, inc_ports = True, layer = layer, corners=corners, bend_radius=br)

    return segment

'''
#make an absorber (this is NOT the pyramid type!!!! there is only one length of meander.)
def absorber_old(numseg=5, lw=2, length=16, center_spacing=4, layer=0):

    absorber = phidl.Device(name='absorber')
    half_absorber = phidl.Device(name='half_absorber')

    #make a line of segments
    segment = absorber_segment(lw=lw, length=length, layer=layer)
    refs_left = [half_absorber.add_ref(segment).movey(i*4*lw) for i in range(num_unit)]

    #add end connector at bottom
    end_connector = geo.rectangle((center_spacing/2., lw))
    end_ref = half_absorber.add_ref(end_connector).movex(length)

    #mirror the half absorber
    x_center = length+center_spacing/2.
    left_ref = absorber.add_ref(half_absorber)
    right_ref = absorber.add_ref(half_absorber).mirror(p1=[x_center, 0], p2=[x_center, 4*lw*num_unit] )
    left_ref.movex(-x_center)
    right_ref.movex(-x_center)

    #ports
    port_x = center_spacing/2.+ lw/2.
    port_y = num_unit * 4 * lw
    absorber.add_port(name = 'abs_1', midpoint = (-port_x, port_y), orientation = 90.)
    absorber.add_port(name = 'abs_2', midpoint = (port_x, port_y), orientation = 90.)


    return absorber
'''


#make an absorber (this is NOT the pyramid type!!!! there is only one length of meander.)
def absorber(num_unit=10, lw=2, start_length=16, function=None, center_spacing=4, layer=None):

    # if no function is defined, make it straight.
    if not function: function = lambda u, start_length: start_length

    absorber = phidl.Device(name='absorber')
    half_absorber = phidl.Device(name='half_absorber')

    #make half of the absorber
    segment = absorber_segment(lw=lw, start_length=start_length, center_spacing=center_spacing, function=function, layer=layer, num_unit=num_unit)
    left_ref = absorber.add_ref(segment)
    right_ref = absorber.add_ref(segment).mirror(p1=[0, 0], p2=[0,1] )

    #ports
    port_x = right_ref.ports["polypath2"].midpoint[0]
    port_y = num_unit * 4 * lw - 3*lw/2.
    absorber.add_port(name = 'abs_1', midpoint = (-port_x, port_y), orientation = 90.)
    absorber.add_port(name = 'abs_2', midpoint = (port_x, port_y), orientation = 90.)


    return absorber

#connectors ------------------------------------------------
def square(side, layer):
    D=phidl.Device()
    s=geo.rectangle((side, side), layer=layer)
    D.add_port(name='p1', midpoint=(side/2., side/2.), orientation=-90)
    return D

#x absorber to upper idc path
def x_idc_to_abs_path(x_abs_pars, x_rcap_pars, x_abs_ref, x_rcap_ref, layer=None):

    D=phidl.Device()

    points=[]
    points.append(x_rcap_ref.ports['idc_2'].midpoint)

    #get the slope of the cap rail line
    rise = x_rcap_ref.ports['idc_2'].midpoint[1] -  x_rcap_ref.ports['idc_1'].midpoint[1]
    run = x_rcap_ref.ports['idc_2'].midpoint[0] -  x_rcap_ref.ports['idc_1'].midpoint[0]
    slope = rise/run
    #append a point slightly down the line to make the path hit the rail at a 90 degree angle
    xrun=10
    points.append([x_rcap_ref.ports['idc_2'].midpoint[0]+xrun, x_rcap_ref.ports['idc_2'].midpoint[1]+xrun*slope])

    radius_tolerance = 20*x_abs_pars["lw"]
    arc_radius = x_rcap_pars["outer_radius"] - x_rcap_pars["numtines"]*(x_rcap_pars["tine_linewidth"] + x_rcap_pars["tine_spacing"]) - x_rcap_pars["tine_spacing"] - x_rcap_pars["rail_extend_in"]
    arc_radius -= radius_tolerance

    abs_end_length = x_abs_pars["function"](x_abs_pars["num_unit"], x_abs_pars["start_length"])
    arc_subtract_angle = 180*(x_abs_pars["lw"]+x_abs_pars["center_spacing"]/2. + abs_end_length)/(pi*arc_radius)
    arc_start_angle = x_rcap_pars['start_angle'] - x_rcap_pars["rail_width"]/(2*pi*arc_radius)
    #append point at intersection of arc and rail radial line
    points.append([arc_radius*cos(radians(arc_start_angle)), arc_radius*sin(radians(arc_start_angle))])

    arc_angle = x_rcap_pars["theta"]/2. - arc_subtract_angle
    steps=50
    angle_step = arc_angle/steps
    for i in range(3,steps-3): points.append([arc_radius*cos(radians(arc_start_angle+i*angle_step)), arc_radius*sin(radians(arc_start_angle+i*angle_step))])

    points.append([-arc_radius, x_abs_ref.ports['abs_2'].midpoint[1]])
    points.append(x_abs_ref.ports['abs_2'].midpoint)
    
    br = x_rcap_pars["rail_width"]
    path=polypath_from_points(xypoints = points, lw = x_rcap_pars["rail_width"], name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    D.add_ref(path)

    extra_al = geo.rectangle((50, x_rcap_pars["rail_width"]+2), layer=x_abs_pars["layer"])
    extra_al_ref = D.add_ref(extra_al).move(x_abs_ref.ports['abs_2'].midpoint).movex(-50).movey(-(x_rcap_pars["rail_width"]+2)/2.)

    return D


#x idc to x absorber
#now with symmetric wiring
def x_idc_to_abs_path_2(x_abs_pars, x_rcap_pars, x_abs_ref, x_rcap_ref, layer=None):

    D=phidl.Device()

    points=[]
    points.append(x_rcap_ref.ports['idc_2'].midpoint)

    #get the slope of the cap rail line
    rise = x_rcap_ref.ports['idc_2'].midpoint[1] -  x_rcap_ref.ports['idc_1'].midpoint[1]
    run = x_rcap_ref.ports['idc_2'].midpoint[0] -  x_rcap_ref.ports['idc_1'].midpoint[0]
    slope = rise/run
    #append a point slightly down the line to make the path hit the rail at a 90 degree angle
    xrun=10
    points.append([x_rcap_ref.ports['idc_2'].midpoint[0]+xrun, x_rcap_ref.ports['idc_2'].midpoint[1]+xrun*slope])

    
    #arc going up to the y region
    radius_tolerance = 20*x_abs_pars["lw"]
    arc_radius_1 = x_rcap_pars["outer_radius"] - x_rcap_pars["numtines"]*(x_rcap_pars["tine_linewidth"] + x_rcap_pars["tine_spacing"]) - x_rcap_pars["tine_spacing"] - x_rcap_pars["rail_extend_in"]
    arc_radius_1 -= radius_tolerance

    arc_start_angle = x_rcap_pars['start_angle'] - x_rcap_pars["rail_width"]/(2*pi*arc_radius_1)
    #append point at intersection of arc and rail radial line
    points.append([arc_radius_1*cos(radians(arc_start_angle)), arc_radius_1*sin(radians(arc_start_angle))])

    outer_arc_angle = x_rcap_pars["theta"]/2. - 85
    steps=50
    angle_step = outer_arc_angle/steps
    for i in range(3,steps): points.append([arc_radius_1*cos(radians(arc_start_angle+i*angle_step)), arc_radius_1*sin(radians(arc_start_angle+i*angle_step))])



    #arc coming back to the absorber
    radius_separation = 40*x_abs_pars["lw"]
    arc_radius_2 = arc_radius_1 - radius_separation

    #append a point on the inner arc right below the last one on the outer arc
    last_angle = arc_start_angle+(steps-1.5)*angle_step
    points.append([arc_radius_2*cos(radians(last_angle)), arc_radius_2*sin(radians(last_angle))])

    abs_end_length = x_abs_pars["function"](x_abs_pars["num_unit"], x_abs_pars["start_length"])
    arc_subtract_angle = 180*(x_abs_pars["lw"]+x_abs_pars["center_spacing"]/2. + abs_end_length)/(pi*arc_radius_2)
    arc_start_angle_2 = arc_start_angle + outer_arc_angle

    arc_angle = 85 -  arc_subtract_angle
    steps=50
    angle_step = arc_angle/steps
    for i in range(3,steps-3): points.append([arc_radius_2*cos(radians(arc_start_angle_2+i*angle_step)), arc_radius_2*sin(radians(arc_start_angle_2+i*angle_step))])

    points.append([-arc_radius_2, x_abs_ref.ports['abs_2'].midpoint[1]])
    points.append(x_abs_ref.ports['abs_2'].midpoint)
    
    br = x_rcap_pars["rail_width"]
    path=polypath_from_points(xypoints = points, lw = x_rcap_pars["rail_width"], name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    D.add_ref(path)

    extra_al = geo.rectangle((50, x_rcap_pars["rail_width"]+2), layer=x_abs_pars["layer"])
    extra_al_ref = D.add_ref(extra_al).move(x_abs_ref.ports['abs_2'].midpoint).movex(-50).movey(-(x_rcap_pars["rail_width"]+2)/2.)

    return D

#lower y absorber to upper y absorber
def y_abs_to_abs_path(y_abs_pars, y_abs_ref_upper, y_abs_ref_lower, layer=None):

    lw=6
    D = phidl.Device()

    points=[]
    points.append(y_abs_ref_lower.ports['abs_1'].midpoint)

    radius_separation = 40*y_abs_pars["lw"]
    arc_radius = y_abs_ref_upper.ports['abs_2'].midpoint[1] + radius_separation
    points.append([y_abs_ref_lower.ports['abs_1'].midpoint[0], -arc_radius])

    abs_end_length = y_abs_pars["function"](y_abs_pars["num_unit"], y_abs_pars["start_length"])
    arc_subtract_angle = 180*(y_abs_pars["lw"]+y_abs_pars["center_spacing"]/2.+abs_end_length)/(pi*arc_radius)
    arc_start_angle = -90 + arc_subtract_angle
    arc_angle = 180 - arc_subtract_angle
    steps=50
    angle_step = arc_angle/steps
    for i in range(2,steps-2): points.append([arc_radius*cos(radians(arc_start_angle+i*angle_step)), arc_radius*sin(radians(arc_start_angle+i*angle_step))])

    points.append([y_abs_ref_upper.ports['abs_2'].midpoint[0], arc_radius])
    points.append(y_abs_ref_upper.ports['abs_2'].midpoint)
    
    br = 5*y_abs_pars["lw"]
    path=polypath_from_points(xypoints = points, lw = lw, name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    D.add_ref(path)

    extra_al = geo.rectangle((lw+2, 50), layer=y_abs_pars["layer"])
    extra_al_ref_upper = D.add_ref(extra_al).move(y_abs_ref_upper.ports['abs_2'].midpoint).movex(-(lw+2)/2)
    extra_al_ref = D.add_ref(extra_al).move(y_abs_ref_lower.ports['abs_1'].midpoint).movex(-(lw+2)/2).movey(-50)

    return D


#y absorber to upper idc path
def y_idc_to_abs_path(y_abs_pars, y_rcap_pars, y_abs_ref, y_rcap_ref, layer=None):

    D = phidl.Device()

    points=[]
    points.append(y_abs_ref.ports['abs_2'].midpoint)

    radius_tolerance = 20*y_abs_pars["lw"]
    arc_radius = y_rcap_pars["outer_radius"] - y_rcap_pars["numtines"]*(y_rcap_pars["tine_linewidth"] + y_rcap_pars["tine_spacing"]) - y_rcap_pars["tine_spacing"] - y_rcap_pars["rail_extend_in"]
    arc_radius -= radius_tolerance
    points.append([y_abs_ref.ports['abs_2'].midpoint[0], -arc_radius])

    arc_start_angle = 270 + 180*(y_abs_pars["lw"]+y_abs_pars["center_spacing"]/2.)/(pi*arc_radius)
    arc_end_angle = y_rcap_pars['start_angle']
    arc_angle = arc_end_angle - arc_start_angle
    steps=50
    angle_step = arc_angle/steps
    for i in range(steps): points.append([arc_radius*cos(radians(arc_start_angle+i*angle_step)), arc_radius*sin(radians(arc_start_angle+i*angle_step))])

    points.append([arc_radius*cos(radians(y_rcap_pars["start_angle"])), arc_radius*sin(radians(y_rcap_pars["start_angle"]))])

    #get the slope of the cap rail line
    rise = y_rcap_ref.ports['idc_2'].midpoint[1] -  y_rcap_ref.ports['idc_1'].midpoint[1]
    run = y_rcap_ref.ports['idc_2'].midpoint[0] -  y_rcap_ref.ports['idc_1'].midpoint[0]
    slope = rise/run
    #append a point slightly down the line to make the path hit the rail at a 90 degree angle
    xrun=10
    points.append([y_rcap_ref.ports['idc_2'].midpoint[0]-xrun, y_rcap_ref.ports['idc_2'].midpoint[1]-xrun*slope])


    points.append(y_rcap_ref.ports['idc_2'].midpoint)
    
    br = 5*y_abs_pars["lw"]
    path=polypath_from_points(xypoints = points, lw = y_rcap_pars["rail_width"], name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    D.add_ref(path)

    extra_al = geo.rectangle((y_rcap_pars["rail_width"]+2, 50), layer=y_abs_pars["layer"])
    extra_al_ref = D.add_ref(extra_al).move(y_abs_ref.ports['abs_2'].midpoint).movex(-(y_rcap_pars["rail_width"]+2)/2.).movey(-50)

    return D


#x idc to coupling capacitor
def x_rcap_to_ccap(x_rcap_ref, x_ccap_ref, x_rcap_pars, layer=None):

    points=[]
    points.append(x_ccap_ref.ports['idc_2'].midpoint)

    radius_tolerance = 20*x_rcap_pars["tine_linewidth"]
    arc_radius = x_rcap_pars["outer_radius"] + x_rcap_pars["rail_extend_out"] + radius_tolerance
    points.append([x_ccap_ref.ports['idc_1'].midpoint[0], arc_radius])

    arc_start_angle = 90.1 + 180*(x_rcap_pars["rail_width"]/2.)/(pi*arc_radius) #weird stuff happening when I just use 90... no idea why.
    arc_end_angle = x_rcap_pars["start_angle"]
    arc_angle = arc_end_angle - arc_start_angle
    steps=50
    angle_step = arc_angle/steps
    for i in range(2,steps-2): 
        points.append([arc_radius*cos(radians(arc_start_angle+i*angle_step)), arc_radius*sin(radians(arc_start_angle+i*angle_step))])

    points.append([arc_radius*cos(radians(x_rcap_pars["start_angle"])), arc_radius*sin(radians(x_rcap_pars["start_angle"]))])

    #get the slope of the cap rail line
    rise = x_rcap_ref.ports['idc_2'].midpoint[1] -  x_rcap_ref.ports['idc_1'].midpoint[1]
    run = x_rcap_ref.ports['idc_2'].midpoint[0] -  x_rcap_ref.ports['idc_1'].midpoint[0]
    slope = rise/run
    #append a point slightly down the line to make the path hit the rail at a 90 degree angle
    xrun=10
    points.append([x_rcap_ref.ports['idc_1'].midpoint[0]-xrun, x_rcap_ref.ports['idc_1'].midpoint[1]-xrun*slope])


    points.append(x_rcap_ref.ports['idc_1'].midpoint)

    br = 2*x_rcap_pars["rail_width"]
    path=polypath_from_points(xypoints = points, lw = x_rcap_pars["rail_width"], name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    return path

#y idc to coupling capacitor
def y_rcap_to_ccap(y_rcap_ref, y_ccap_ref, y_rcap_pars, y_ccap_pars, layer=None):

    points=[]
    #points.append(y_ccap_ref.ports['idc_4'].midpoint)
    points.append(y_ccap_ref.ports['idc_3'].midpoint)

    radius_tolerance = 20*y_rcap_pars["tine_linewidth"]
    arc_radius = y_rcap_pars["outer_radius"] + y_rcap_pars["rail_extend_out"] + radius_tolerance

    #intersection of arc with cap rail
    arc_y_start = np.sqrt(arc_radius**2 - (y_ccap_ref.ports['idc_3'].midpoint[0])**2)
    points.append([y_ccap_ref.ports['idc_3'].midpoint[0], -1*arc_y_start])

    ccap_width = y_ccap_pars["rail_width"]/2. + y_ccap_pars["tine_length"] + y_ccap_pars["tine_spacing"]
    arc_start_angle = 270 + 180*(ccap_width)/(pi*arc_radius) 
    arc_end_angle = y_rcap_pars["start_angle"]
    arc_angle = arc_end_angle - arc_start_angle
    steps=50
    angle_step = arc_angle/steps

    for i in range(3,steps-4): 
        points.append([arc_radius*cos(radians(arc_start_angle+i*angle_step)), arc_radius*sin(radians(arc_start_angle+i*angle_step))])

    points.append([arc_radius*cos(radians(y_rcap_pars["start_angle"])), arc_radius*sin(radians(y_rcap_pars["start_angle"]))])

    #get the slope of the cap rail line
    rise = y_rcap_ref.ports['idc_2'].midpoint[1] -  y_rcap_ref.ports['idc_1'].midpoint[1]
    run = y_rcap_ref.ports['idc_2'].midpoint[0] -  y_rcap_ref.ports['idc_1'].midpoint[0]
    slope = rise/run
    #append a point slightly down the line to make the path hit the rail at a 90 degree angle
    xrun=10
    points.append([y_rcap_ref.ports['idc_1'].midpoint[0]+xrun, y_rcap_ref.ports['idc_1'].midpoint[1]+xrun*slope])


    points.append(y_rcap_ref.ports['idc_1'].midpoint)

    br = 2*y_rcap_pars["rail_width"]
    path=polypath_from_points(xypoints = points, lw = y_rcap_pars["rail_width"], name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)

    return path


## ---------------------------------------------------------------------------------------------------------------------------

#feedline for optical chip
def optical_feedline(feed_pars):

    line = phidl.Device()
    layer = feed_pars["layer"]

    lw=feed_pars["lw"]
    pix_radius=feed_pars["pix_radius"]
    pix_offset=feed_pars["pix_offset"]
    feedline_separation=feed_pars["feedline_separation"]

    pix_1_center = np.array([pix_offset, pix_offset])
    pix_2_center = np.array([-pix_offset, pix_offset])
    pix_3_center = np.array([-pix_offset, -pix_offset])
    pix_4_center = np.array([pix_offset, -pix_offset])

    sep = pix_radius + feedline_separation
    points = []

    #main feedline
    points.append(np.add(pix_2_center, [-sep+feedline_separation, sep]))
    points.append(np.add(pix_1_center, [sep, sep]))

    points.append(np.add(pix_1_center, [sep, -sep]))
    points.append(np.add(pix_2_center, [-sep, -sep]))

    points.append(np.add(pix_3_center, [-sep, sep]))
    points.append(np.add(pix_4_center, [sep, sep]))

    points.append(np.add(pix_4_center, [sep, -sep]))
    points.append(np.add(pix_3_center, [-sep+feedline_separation, -sep]))

    br = 500
    path=polypath_from_points(xypoints = points, lw = lw, name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)
    path_ref = line.add_ref(path)

    #feedline to pad
    to_pad_points = []
    to_pad_points.append(np.add(pix_2_center, [-sep+feedline_separation, sep]))
    to_pad_points.append(np.add(pix_2_center, [-sep, sep]))
    to_pad_points.append(np.add(pix_2_center, [-sep, sep+1.5*feedline_separation]))
    to_pad_points.append([0, pix_offset+sep+1.5*feedline_separation])
    to_pad_points.append([0, pix_offset+sep+2*feedline_separation+350])

    pad_br = 500
    pad_path=polypath_from_points(xypoints = to_pad_points, lw = lw, name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=pad_br)
    pad_path_upper_ref=line.add_ref(pad_path)
    pad_path_lower_ref=line.add_ref(pad_path).mirror(p1=[0,0], p2=[1,0])

    line.add_port(name='p1', midpoint=(0, pix_offset+sep+2*feedline_separation+350), orientation=90)
    line.add_port(name='p2', midpoint=(0, -pix_offset-sep-2*feedline_separation-350), orientation=-90)

    return line


#feedline for optical chip
def dark_feedline(feed_pars):

    line = phidl.Device()
    layer = feed_pars["layer"]

    lw=feed_pars["lw"]
    pix_radius=feed_pars["pix_radius"]
    pix_spacing=feed_pars["pix_spacing"]
    feedline_separation=feed_pars["feedline_separation"]

    pix_1_center = np.array([-2*pix_spacing, 0])
    pix_6_center = np.array([2*pix_spacing, 0])

    sep = pix_radius + feedline_separation
    points = []

    #main feedline
    first_point = [pix_1_center[0]-2400,2750]
    second_point = [pix_1_center[0]-2000,2750]
    points.append(first_point)
    points.append(second_point)

    points.append(np.add(pix_1_center, [-sep+feedline_separation, sep]))
    points.append(np.add(pix_6_center, [sep, sep]))

    points.append(np.add(pix_6_center, [sep, -sep]))
    points.append(np.add(pix_1_center, [-sep+feedline_separation, -sep]))

    second_to_last_point = [pix_1_center[0]-2000, -2750]
    last_point = [pix_1_center[0]-2400,-2750]
    points.append(second_to_last_point)
    points.append(last_point)

    br = 500
    path=polypath_from_points(xypoints = points, lw = lw, name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=br)
    path_ref = line.add_ref(path)

    '''
    #feedline to pad
    to_pad_points = []
    to_pad_points.append(np.add(pix_1_center, [-sep+feedline_separation, sep]))
    #to_pad_points.append(np.add(pix_1_center, [-sep, sep]))
    #to_pad_points.append(np.add(pix_1_center, [-sep, sep+2*feedline_separation]))
    #to_pad_points.append([0, sep+2*feedline_separation])
    #to_pad_points.append([0, sep+3*feedline_separation])

   # pad_br = 500
    #pad_path=polypath_from_points(xypoints = to_pad_points, lw = lw, name = None, inc_ports = True, layer = layer, corners="circular bend", bend_radius=pad_br)
   # pad_path_upper_ref=line.add_ref(pad_path)
   # pad_path_lower_ref=line.add_ref(pad_path).mirror(p1=[0,0], p2=[1,0])
    '''

    line.add_port(name='p1', midpoint=(first_point), orientation=180)
    line.add_port(name='p2', midpoint=(last_point), orientation=180)

    return line

def feedline_pad(feed_pars):

    pad = phidl.Device()

    square = geo.rectangle((feed_pars["pad_sidelength"], feed_pars["pad_sidelength"]), layer=feed_pars["layer"])
    square_ref=pad.add_ref(square).movex(feed_pars["trans_length"]).movey(-feed_pars["pad_sidelength"]/2.)

    taper = geo.taper(length = feed_pars["trans_length"], width1 = feed_pars["lw"], width2 = feed_pars["pad_sidelength"], layer = feed_pars["layer"])
    taper_ref = pad.add_ref(taper)

    pad.add_port(name='p1', midpoint=(0,0), orientation=180)

    return pad


def x_feed_connect(pix_ref, lw, feedline_separation, feed_lw, layer=None):
    points = [pix_ref.ports["x"].midpoint, [pix_ref.ports["x"].midpoint[0], pix_ref.ports["x"].midpoint[1] + feedline_separation - feed_lw/2.]]
    path=polypath_from_points(xypoints = points, lw = lw, layer = layer, inc_ports=False)
    return path

def y_feed_connect(pix_ref, lw, feedline_separation, feed_lw, layer=None):
    points = [pix_ref.ports["y"].midpoint, [pix_ref.ports["y"].midpoint[0], pix_ref.ports["y"].midpoint[1] - feedline_separation + feed_lw/2.]]
    path=polypath_from_points(xypoints = points, lw = lw, layer = layer, inc_ports=False)
    return path


#chip outlines and other stuff

def get_logos(layer):

    anllogofile = 'logos/anl_logo.gds'
    uclogofile  = 'logos/uc_logo.gds'

    sf = 0.75
    anllogo = geo.import_gds(anllogofile, cellname = None, flatten = False)
    [p.scale(sf,sf, anllogo.center) for p in anllogo.polygons]
    uclogo  = geo.import_gds(uclogofile,  cellname = None, flatten = False)
    [p.scale(sf,sf, uclogo.center) for p in uclogo.polygons]

    anllogo.remap_layers(layermap = {0: layer} )
    uclogo.remap_layers(layermap = {0: layer} )

    return anllogo, uclogo


def optical_chip_outline(dev_label, chip_pars):

    outline = phidl.Device(name="outline")

    l=chip_pars["chip_sidelength"]
    w=chip_pars["outline_width"]
    o=chip_pars["outline_offset"]
    
    horizontal = geo.rectangle((l, w), layer=chip_pars['line_layer'])
    upper=outline.add_ref(horizontal).movex(-l/2.).movey(l/2.-o)
    lower=outline.add_ref(horizontal).movex(-l/2.).movey(-l/2.+o-w)
    vertical = geo.rectangle((w, l), layer=chip_pars['line_layer'])
    left=outline.add_ref(vertical).movex(-l/2.+o-w).movey(-l/2.)
    right=outline.add_ref(vertical).movex(l/2.-o).movey(-l/2.)

    #text
    label_offset=chip_pars["chip_sidelength"]/2.-chip_pars["outline_offset"]-chip_pars["outline_width"]-100
    label = geo.text("SPT4 v3", size=500, layer=chip_pars["text_layer"])
    label_ref=outline.add_ref(label).movex(-label_offset+500).movey(label_offset-1100)

    #text
    dev_label = geo.text(dev_label, size=500, layer=chip_pars["text_layer"])
    dev_label_ref=outline.add_ref(dev_label).movex(label_offset-3500).movey(label_offset-1100)

    #logos
    anllogo, uclogo = get_logos(layer = chip_pars["text_layer"])
    anl_ref = outline.add_ref(anllogo).movex(10000).movey(-11500)
    uc_ref = outline.add_ref(uclogo).movex(6000).movey(-11500.)

    return outline


def dark_chip_outline(dev_label, chip_pars):

    outline = phidl.Device(name="outline")

    sl=chip_pars["chip_sidelength"]
    sw=chip_pars["chip_sidewidth"]
    w=chip_pars["outline_width"]
    o=chip_pars["outline_offset"]
    
    horizontal = geo.rectangle((sl, w), layer=chip_pars['line_layer'])
    upper=outline.add_ref(horizontal).movex(-sl/2.).movey(sw/2.-o)
    lower=outline.add_ref(horizontal).movex(-sl/2.).movey(-sw/2.+o-w)
    vertical = geo.rectangle((w, sw), layer=chip_pars['line_layer'])
    left=outline.add_ref(vertical).movex(-sl/2.+o-w).movey(-sw/2.)
    right=outline.add_ref(vertical).movex(sl/2.-o).movey(-sw/2.)

    #text
    label_offset=chip_pars["chip_sidelength"]/2.-chip_pars["outline_offset"]-chip_pars["outline_width"]-100
    label = geo.text("TLS v1", size=500, layer=chip_pars["text_layer"])
    label_ref=outline.add_ref(label).movex(-label_offset + 500).movey(label_offset/2.-2500)

    #text
    dev_label = geo.text(dev_label, size=500, layer=chip_pars["text_layer"])
    dev_label_ref=outline.add_ref(dev_label).movex(label_offset-3500).movey(label_offset/2.-2500)

    #logos
    anllogo, uclogo = get_logos(layer = chip_pars["text_layer"])
    anl_ref = outline.add_ref(anllogo).movex(10000).movey(-4000)
    uc_ref = outline.add_ref(uclogo).movex(6000).movey(-4000.)

    return outline

def wafer_alignment_marking():

    D = phidl.Device()
    cross = geo.cross(length=300, width=5, layer=0)
    cross_ref = D.add_ref(cross)

    points=[]
    points.append([500,490])
    points.append([500,-500])
    points.append([-500,-500])
    points.append([-500,500])
    points.append([510,500])
    box=polypath_from_points(xypoints = points, lw = 20, inc_ports = False, layer = 0)
    box_ref = D.add_ref(box)

    return D

#test structures for the top of the wafer

def test_structure(test_pars, label, include_boxes=False):

    structure = phidl.Device()

    pad = feedline_pad(test_pars)
    pad_ref_left = structure.add_ref(pad).mirror(p1=(0,0), p2=(0,1)).movex(-test_pars["length"]/2.)
    pad_ref_right = structure.add_ref(pad).movex(test_pars["length"]/2.)

    #make a discontinuous line with boxes on it
    if include_boxes:
        box_offset=np.array([-test_pars["boxw"]/2., -test_pars["boxh"]/2.])
        box_start=np.add(pad_ref_left.ports['p1'].midpoint, box_offset)
        box_midpoints=[ np.add(box_start, np.array([test_pars["length"]*(4+i)/12.,0])) for i in range(4)]
        box = geo.rectangle((test_pars["boxw"], test_pars["boxh"]), layer=test_pars["box_layer"])
        box_refs = [structure.add_ref(box).move(list(box_midpoints[i]) )for i in range(4)]

        points = [pad_ref_left.ports['p1'].midpoint]
        for i in range(4):
            seg_midpoint = np.subtract(box_midpoints[i], box_offset)
            points.append(np.add(seg_midpoint, np.array([-test_pars['boxw']/4.,0])))
            points.append(np.add(seg_midpoint, np.array([test_pars['boxw']/4.,0])))
        points.append(pad_ref_right.ports['p1'].midpoint)

        for i in range(5):
            point_pair = points[2*i:2*i+2]
            seg = polypath_from_points(xypoints = point_pair, lw = test_pars["lw"], layer = test_pars["layer"])
            seg_ref = structure.add_ref(seg)

    #just make a continuous line
    else:  
        points = [pad_ref_left.ports['p1'].midpoint, pad_ref_right.ports['p1'].midpoint]
        line = polypath_from_points(xypoints = points, lw = test_pars["lw"], layer = test_pars["layer"])
        line_ref = structure.add_ref(line)

    text = geo.text(label, size=500, layer = test_pars["layer"])
    text_ref = structure.add_ref(text).movey(test_pars["pad_sidelength"])

    return structure


def test_structure_2(pad_layer, line_layer, label, line=True):
    D = phidl.Device()
    pad = geo.rectangle((3000,1000), layer=pad_layer)
    left = D.add_ref(pad).movex(-3200)
    right = D.add_ref(pad).movex(200)
    if line: 
        line = geo.rectangle((500, 50), layer=line_layer)
        line_ref = D.add_ref(line).movex(-250).movey(475)

    text = geo.text(label, size=500, layer = pad_layer)
    text_ref = D.add_ref(text).movey(1500)
    return D

#--------------------------------
def liftoff_mask(x_abs_pars, layer):
    liftoff_radius = x_abs_pars["num_unit"]*2*x_abs_pars["lw"] + 25
    liftoff_circle = geo.circle(radius=liftoff_radius, layer=layer)
    notch_x = geo.rectangle((25,10), layer=layer).movex(-liftoff_radius-2).movey(-5)
    notch_x_extra = geo.rectangle((25,10), layer=layer).movex(liftoff_radius+2-25).movey(-5)
    notch_yhi = geo.rectangle((10,25), layer=layer).movey(liftoff_radius+2-25).movex(-5)
    notch_ylo = geo.rectangle((10,25), layer=layer).movey(-liftoff_radius-2).movex(-5)
    D = geo.boolean(A = liftoff_circle, B = [notch_x, notch_x_extra, notch_ylo, notch_yhi], operation = 'A-B')
    return D