#Generate a single pixel
#Do not change anything without first checking to see if it's a variable in settings.py

import components as comp
from math import pi
from matplotlib import pyplot as plt
from phidl import Device
from phidl import geometry as geo
from phidl.quickplotter import quickplot as qp
from pys4fab.core import tools

import settings
layers = settings.get_layers()
pixel_settings = settings.get_pixel_settings()

full_pixel_radius = pixel_settings["full_pixel_radius"]
membrane_radius = pixel_settings["membrane_radius"]
x_rcap_pars = pixel_settings["x_rcap_pars"]
y_rcap_pars = pixel_settings["y_rcap_pars"]
ccap_pars = pixel_settings["ccap_pars"]
x_abs_pars = pixel_settings["x_abs_pars"]
y_abs_pars = pixel_settings["y_abs_pars"]


def create_pixel(x_tine_length, y_tine_length, cap_layer=None, abs_layer=None, double_space=False):

	#assign layers
	x_rcap_pars["layer"] = cap_layer
	y_rcap_pars["layer"] = cap_layer
	x_abs_pars["layer"] = abs_layer
	y_abs_pars["layer"] = abs_layer

	#double spacing feature
	if double_space:
		x_rcap_pars["tine_spacing"]*=2
		y_rcap_pars["tine_spacing"]*=2
		x_rcap_pars["outer_radius"]*=1.2
		y_rcap_pars["outer_radius"]*=1.2

	#calculate angles
	x_width = x_rcap_pars["numtines"]*(x_rcap_pars["tine_linewidth"]+x_rcap_pars["tine_spacing"]) - x_rcap_pars["tine_spacing"]
	x_theta = 360*x_tine_length/(pi*(2*x_rcap_pars["outer_radius"] - x_width)) 
	y_width = y_rcap_pars["numtines"]*(y_rcap_pars["tine_linewidth"]+y_rcap_pars["tine_spacing"]) - y_rcap_pars["tine_spacing"]
	y_theta = 360*y_tine_length/(pi*(2*y_rcap_pars["outer_radius"] - y_width)) 

	x_rcap_pars['theta'] = x_theta
	x_rcap_pars['start_angle'] = 180 - x_theta/2.
	y_rcap_pars['theta'] = y_theta
	y_rcap_pars['start_angle'] = 360 - y_theta/2.

	D = Device('test')

	#create resonator capacitors
	x_rcap = comp.arc_idc(**x_rcap_pars)
	y_rcap = comp.arc_idc(**y_rcap_pars)

	#create coupling capacitors
	#some shady tricks with layers
	ccap_pars["layer_1"] = cap_layer
	ccap_pars["layer_2"] = layers["nb_base"]
	x_ccap = comp.rect_idc(**ccap_pars)
	ccap_pars["layer_2"] = cap_layer
	ccap_pars["layer_1"] = layers["nb_base"]
	y_ccap = comp.rect_idc(**ccap_pars)
	ccap_pars["layer_1"] = cap_layer
	ccap_pars["layer_2"] = layers["nb_base"]

	#create absorbers
	x_abs = comp.absorber(**x_abs_pars)
	y_abs = comp.absorber(**y_abs_pars)

	#place resonator capacitors
	x_rcap_ref=D.add_ref(x_rcap)
	y_rcap_ref=D.add_ref(y_rcap)

	#place coupling capacitors
	cap_length = ccap_pars["numtines"]*(ccap_pars["tine_linewidth"]+ccap_pars["tine_spacing"]) - ccap_pars["tine_spacing"]
	x_ccap_ref=D.add_ref(x_ccap).movey(x_rcap_pars["outer_radius"])
	y_ccap_ref=D.add_ref(y_ccap).movey(-y_rcap_pars["outer_radius"]-cap_length)

	#place absorbers
	x_abs_ref = D.add_ref(x_abs).rotate(90).movex(x_abs_pars["num_unit"]*2*x_abs_pars["lw"])
	y_abs_ref_lower = D.add_ref(y_abs).rotate(180).movey(- x_abs_pars["start_length"] - 2*x_abs_pars["center_spacing"])
	y_abs_ref_upper = D.add_ref(y_abs).movey(x_abs_pars["start_length"] + 2*x_abs_pars["center_spacing"])


	#connectors -------------------------------------------------------

	#connect x absorber to x rcap
	x_connect = comp.x_idc_to_abs_path_2(x_abs_pars, x_rcap_pars, x_abs_ref, x_rcap_ref, layer=cap_layer)
	x_connect_upper_ref = D.add_ref(x_connect)
	x_connect_lower_ref = D.add_ref(x_connect)
	x_connect_lower_ref.mirror(p1=[0,0], p2=[-1,0])

	#connect y absorbers to each other
	y_abs_connect = comp.y_abs_to_abs_path(y_abs_pars, y_abs_ref_upper, y_abs_ref_lower, layer=cap_layer)
	y_abs_connect_ref = D.add_ref(y_abs_connect)

	#connect y absorbers to y rcap
	y_connect = comp.y_idc_to_abs_path(y_abs_pars, y_rcap_pars, y_abs_ref_lower, y_rcap_ref, layer=cap_layer)
	y_connect_lower_ref = D.add_ref(y_connect)
	y_connect_upper_ref = D.add_ref(y_connect)
	y_connect_upper_ref.mirror(p1=[0,0], p2=[-1,0])

	#connect x rcap to x ccap
	x_cap_connect = comp.x_rcap_to_ccap(x_rcap_ref, x_ccap_ref, x_rcap_pars, layer=cap_layer)
	x_cap_connect_ref = D.add_ref(x_cap_connect)

	#connect y rcap to y ccap
	y_cap_connect = comp.y_rcap_to_ccap(y_rcap_ref, y_ccap_ref, y_rcap_pars, ccap_pars, layer=cap_layer)
	y_cap_connect_ref = D.add_ref(y_cap_connect)

	#extend coupling capacitors for eventual feedline connection
	x_feed_points=[x_ccap_ref.ports['idc_4'].midpoint, [x_ccap_ref.ports['idc_4'].midpoint[0], full_pixel_radius]]
	x_feed_path=tools.polypath_from_points(xypoints = x_feed_points, lw = ccap_pars["rail_width"], inc_ports = True, layer = ccap_pars["layer_2"])
	x_feed_ref = D.add_ref(x_feed_path)

	y_feed_points=[y_ccap_ref.ports['idc_1'].midpoint, [y_ccap_ref.ports['idc_1'].midpoint[0], -full_pixel_radius]]
	y_feed_path=tools.polypath_from_points(xypoints = y_feed_points, lw = ccap_pars["rail_width"], inc_ports = True, layer = ccap_pars["layer_2"])
	y_feed_ref = D.add_ref(y_feed_path)

	#ports
	D.add_port( name = "x", midpoint = x_feed_ref.ports["polypath2"].midpoint, orientation = 90 )
	D.add_port( name = "y", midpoint = y_feed_ref.ports["polypath2"].midpoint, orientation = -90 )

	#circle showing where the membrane will be
	membrane = geo.circle(radius=membrane_radius, layer=layers["drill_si_backside"])
	membrane_ref = D.add_ref(membrane)

	#REMOVE THIS UNLESS NEEDED FOR ANL LIFTOFF PROCESS
	#circle to cover al for nb liftoff procedure
	#liftoff = comp.liftoff_mask(x_abs_pars, layer=layers["tabs"])
	#liftoff_ref = D.add_ref(liftoff)

	#liftoff_radius = x_abs_pars["num_unit"]*2*x_abs_pars["lw"] + 25
	#liftoff_2 = geo.circle(radius=liftoff_radius, layer=layers["liftoff_b"])
	#D.add_ref(liftoff_2)

	#-------------------------------------------------------------------------
	#double spacing feature (Undo the damage - do not change this.)
	if double_space:
		x_rcap_pars["tine_spacing"]/=2
		y_rcap_pars["tine_spacing"]/=2
		x_rcap_pars["outer_radius"]/=1.2
		y_rcap_pars["outer_radius"]/=1.2

	return D


# Turn on to plot the pixel alone

#D = create_pixel(600, 600, cap_layer=0, abs_layer=1)
#qp(D)
#plt.show()
