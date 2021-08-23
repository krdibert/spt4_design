#Generate an SPT4 dark chip
#Do not change anything without first checking to see if it's a variable in settings.py

import components as comp
from math import pi
from matplotlib import pyplot as plt
from phidl import Device
from phidl import geometry as geo
from phidl.quickplotter import quickplot as qp

from pys4fab.core import tools
from create_pixel import create_pixel

import settings
layers = settings.get_layers()
pars = settings.get_dark_chip_settings()

chip_pars = pars["chip_pars"]
feed_pars = pars["feed_pars"]
rail_width = pars["rail_width"]


# -----------------------------------------------------------------------------



def create_dark_chip(dev_label,cap_angles, double_space=False):

	D=Device()

	pix_spacing = feed_pars["pix_spacing"]
	feedline_separation = feed_pars["feedline_separation"]

	#create dark pixels
	pix_d1 = create_pixel(cap_angles['d1_x'], cap_angles['d1_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"], double_space=double_space)
	pix_d1_ref = D.add_ref(pix_d1).movex(-2*pix_spacing)
	pix_d1_x = comp.x_feed_connect(pix_d1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d1_x_ref = D.add_ref(pix_d1_x)
	pix_d1_y = comp.y_feed_connect(pix_d1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d1_y_ref = D.add_ref(pix_d1_y)

	pix_d2 = create_pixel(cap_angles['d2_x'], cap_angles['d2_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"], double_space=double_space)
	pix_d2_ref = D.add_ref(pix_d2).movex(-pix_spacing)
	pix_d2_x = comp.x_feed_connect(pix_d2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d2_x_ref = D.add_ref(pix_d2_x)
	pix_d2_y = comp.y_feed_connect(pix_d2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d2_y_ref = D.add_ref(pix_d2_y)

	pix_d3 = create_pixel(cap_angles['d3_x'], cap_angles['d3_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"], double_space=double_space)
	pix_d3_ref = D.add_ref(pix_d3)#.movex(-pix_spacing/2.)
	pix_d3_x = comp.x_feed_connect(pix_d3_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d3_x_ref = D.add_ref(pix_d3_x)
	pix_d3_y = comp.y_feed_connect(pix_d3_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d3_y_ref = D.add_ref(pix_d3_y)

	pix_d4 = create_pixel(cap_angles['d4_x'], cap_angles['d4_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"], double_space=double_space)
	pix_d4_ref = D.add_ref(pix_d4).movex(pix_spacing)
	pix_d4_x = comp.x_feed_connect(pix_d4_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d4_x_ref = D.add_ref(pix_d4_x)
	pix_d4_y = comp.y_feed_connect(pix_d4_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d4_y_ref = D.add_ref(pix_d4_y)

	pix_d5 = create_pixel(cap_angles['d5_x'], cap_angles['d5_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"], double_space=double_space)
	pix_d5_ref = D.add_ref(pix_d5).movex(2*pix_spacing)
	pix_d5_x = comp.x_feed_connect(pix_d5_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d5_x_ref = D.add_ref(pix_d5_x)
	pix_d5_y = comp.y_feed_connect(pix_d5_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d5_y_ref = D.add_ref(pix_d5_y)
	'''
	pix_d6 = create_pixel(cap_angles['d6_x'], cap_angles['d6_y'])
	pix_d6_ref = D.add_ref(pix_d6).movex(5*pix_spacing/2.)
	pix_d6_x = comp.x_feed_connect(pix_d6_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"])
	pix_d6_x_ref = D.add_ref(pix_d6_x)
	pix_d6_y = comp.y_feed_connect(pix_d6_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"])
	pix_d6_y_ref = D.add_ref(pix_d6_y)
	'''
	
	#create feedline
	feed = comp.dark_feedline(feed_pars)
	feed_ref = D.add_ref(feed)

	
	#create terminal pads
	pad = comp.feedline_pad(feed_pars)
	pad_upper_ref = D.add_ref(pad)
	pad_lower_ref = D.add_ref(pad)
	pad_upper_ref.connect(port='p1', destination=feed_ref.ports['p1'])
	pad_lower_ref.connect(port='p1', destination=feed_ref.ports['p2'])
	

	#create box outline and text labels
	outline = comp.dark_chip_outline(dev_label, chip_pars)
	outline_ref = D.add_ref(outline)


	return D



