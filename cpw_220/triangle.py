#812 detector triangle on a 4 inch wafer for uc fab
#NOT READY FOR FAB. The frequency scheduling has not been done!

from math import pi
from matplotlib import pyplot as plt
import numpy as np
from phidl import Device
from phidl import geometry as geo
import phidl.path as pp
from phidl.quickplotter import quickplot as qp

#from pys4fab.core import tools
#from create_array_pixel import create_array_pixel as create_pixel

import components as comp
from cpw_toolkit import tile, place_pixels, connect_feedlines_tri

import settings
layers = settings.get_layers()
wafer_pars=settings.get_wafer_settings()

triangle=[
'--------------Z',
'--------------IN',
'-------------HZH',
'-------------NINI',
'------------ZHZHZ',
'------------INININ',
'-----------HZHZHZH',
'-----------NINININI',
'----------ZHZHZHZHZ',
'----------INININININ',
'---------HZHZHZHZHZH',
'---------NINININININI',
'--------ZHZHZHZHZHZHZ',
'--------INININININININ',
'-------HZHZHZHZHZHZHZH',
'-------NINININININININI',
'------ZHZHZHZHZHZHZHZHZ',
'------INININININININININ',
'-----HZHZHZHZHZHZHZHZHZH',
'-----NINININININININININI',
'----ZHZHZHZHZHZHZHZHZHZHZ',
'----INININININININININININ',
'---HZHZHZHZHZHZHZHZHZHZHZH',
'---NINININININININININININI',
'--ZHZHZHZHZHZHZHZHZHZHZHZHZ',
'--INININININININININININININ',
'-HZHZHZHZHZHZHZHZHZHZHZHZHZH',
'-NINININININININININININININI',
'GGGGGGGGGGGGGGGGGGGGGGGGGGGG']


array = Device()
SUBTRACT_GND = Device()

#set up banks for the resonators (much wider than we actually want in the end)

caps=np.linspace(600,1900,812)

D, F, NO_GND = place_pixels(triangle, caps)
C, N = connect_feedlines_tri(F)

NO_GND.add_ref(N)
D.add_ref(C)


#identify the center point
p1 = F[0][-1]
p2 = F[1][-1]

p3=[p2[0], p1[1]]#middle of base of small end triangle
p4 =  ((p3[0]-p1[0])*2 + p1[0], p3[1]) #tip of end triangle (true triangle end if not for feedlines)

p5 =  ( p1[0] + (p2[0]-p1[0])/2., p1[1] + (p2[1]-p1[1])/2.) #midpoint of p1 and p2


center_x = p5[0] + (p4[0]-p5[0])*1.5
center_y = p5[1] + (p4[1]-p5[1])*1.5

marker=geo.circle(radius=50, layer=layers['nb_base'])
D.add_ref(marker).movex(p4[0]).movey(p4[1])
D.add_ref(marker).movex(center_x).movey(center_y)

#center_x = D.xmax+tile_sidelength
#center_y = D.ymin

#array.add_ref(D).movex(-center_x).movey(-center_y)
#SUBTRACT_GND.add_ref(NO_GND).movex(-center_x).movey(-center_y)



###

print('rotate')
array.add_ref(D).movex(-center_x).movey(-center_y).rotate(-240).movey(40000)
SUBTRACT_GND.add_ref(NO_GND).movex(-center_x).movey(-center_y).rotate(-240).movey(40000)

print('Rendering...')
###

array_rad=70000

gnd_poly_points = [(0,5000),  (np.cos(4*np.pi/3)*array_rad - 5000, np.sin(4*np.pi/3)*array_rad), (np.cos(5*np.pi/3)*array_rad + 5000, np.sin(5*np.pi/3)*array_rad), (0, 5000)]
#GND=geo.circle(radius=wafer_pars["outer_radius"], layer=layers['gnd'])
GND=Device()
GND.add_polygon(gnd_poly_points, layer=layers['gnd']).movey(40000)
gnd_plane = geo.boolean(A=[GND], B=[SUBTRACT_GND], operation='A-B', layer=layers['gnd'])	
array.add_ref(gnd_plane)#

#outer ring
outer_ring=geo.ring(radius=wafer_pars["outer_radius"]-wafer_pars["outer_ring_thickness"]/2., width=wafer_pars["outer_ring_thickness"], layer=layers["edge_bead"])
outer_ring_ref = array.add_ref(outer_ring)

#triangle dicing lines
dicing_points = [(0,5000),  (np.cos(4*np.pi/3)*array_rad - 5000, np.sin(4*np.pi/3)*array_rad), (np.cos(5*np.pi/3)*array_rad + 5000, np.sin(5*np.pi/3)*array_rad), (0, 5000)]
dice = comp.polypath_from_points(xypoints=dicing_points, lw = 200, name = None, inc_ports = True, layer = 3, corners="smooth", bend_radius=50)
array.add_ref(dice).movey(40000)

#alignment markings
align = comp.wafer_alignment_marking()
left_align_ref = array.add_ref(align).movex(-44000)
left_align_ref = array.add_ref(align).movex(44000)

array.write_gds("../../spt4_mask_files/triangle.gds")
