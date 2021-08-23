#Generate an SPT4 optical chip
#Do not change anything without first checking to see if it's a variable in settings.py

import components as comp
from math import pi
from matplotlib import pyplot as plt
from phidl import Device
from phidl import geometry as geo

from pys4fab.core import tools
from create_pixel import create_pixel

import settings
layers = settings.get_layers()
pars = settings.get_optical_chip_settings()

chip_pars = pars["chip_pars"]
feed_pars = pars["feed_pars"]
rail_width = pars["rail_width"]

def create_optical_chip(dev_label, cap_angles):

	D=Device()

	pix_offset = feed_pars["pix_offset"]
	feedline_separation = feed_pars["feedline_separation"]

	#create optical pixels
	pix_1 = create_pixel(cap_angles['p1_x'], cap_angles['p1_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_1_ref = D.add_ref(pix_1).move([pix_offset, pix_offset])
	pix_1_x = comp.x_feed_connect(pix_1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_1_x_ref = D.add_ref(pix_1_x)
	pix_1_y = comp.y_feed_connect(pix_1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_1_y_ref = D.add_ref(pix_1_y)

	pix_2 = create_pixel(cap_angles['p2_x'], cap_angles['p2_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_2_ref = D.add_ref(pix_2).move([-pix_offset, pix_offset])
	pix_2_x = comp.x_feed_connect(pix_2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_2_x_ref = D.add_ref(pix_2_x)
	pix_2_y = comp.y_feed_connect(pix_2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_2_y_ref = D.add_ref(pix_2_y)

	pix_3 = create_pixel(cap_angles['p3_x'], cap_angles['p3_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_3_ref = D.add_ref(pix_3).move([-pix_offset, -pix_offset])
	pix_3_x = comp.x_feed_connect(pix_3_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_3_x_ref = D.add_ref(pix_3_x)
	pix_3_y = comp.y_feed_connect(pix_3_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_3_y_ref = D.add_ref(pix_3_y)

	pix_4 = create_pixel(cap_angles['p4_x'], cap_angles['p4_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_4_ref = D.add_ref(pix_4).move([pix_offset, -pix_offset])
	pix_4_x = comp.x_feed_connect(pix_4_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_4_x_ref = D.add_ref(pix_4_x)
	pix_4_y = comp.y_feed_connect(pix_4_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_4_y_ref = D.add_ref(pix_4_y)

	#create dark pixels
	pix_d1 = create_pixel(cap_angles['d1_x'], cap_angles['d1_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_d1_ref = D.add_ref(pix_d1).move([0, pix_offset])
	pix_d1_x = comp.x_feed_connect(pix_d1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d1_x_ref = D.add_ref(pix_d1_x)
	pix_d1_y = comp.y_feed_connect(pix_d1_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d1_y_ref = D.add_ref(pix_d1_y)

	pix_d2 = create_pixel(cap_angles['d2_x'], cap_angles['d2_y'], cap_layer=layers["nb_base"], abs_layer=layers["al_base"])
	pix_d2_ref = D.add_ref(pix_d2).move([0, -pix_offset])
	pix_d2_x = comp.x_feed_connect(pix_d2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d2_x_ref = D.add_ref(pix_d2_x)
	pix_d2_y = comp.y_feed_connect(pix_d2_ref, lw=rail_width, feedline_separation=feedline_separation, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_d2_y_ref = D.add_ref(pix_d2_y)

	#create single-material pixels
	single_material_feedline_sep = pix_offset - feedline_separation - 2*feed_pars["pix_radius"] + 8 #for 8 micron overlap

	pix_al = create_pixel(cap_angles['al_x'], cap_angles['al_y'], cap_layer=layers["al_base"], abs_layer=layers["al_base"])
	pix_al_ref = D.add_ref(pix_al).move([-pix_offset/2., 0])
	pix_al_x = comp.x_feed_connect(pix_al_ref, lw=rail_width, feedline_separation=single_material_feedline_sep, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_al_x_ref = D.add_ref(pix_al_x)
	pix_al_y = comp.y_feed_connect(pix_al_ref, lw=rail_width, feedline_separation=single_material_feedline_sep, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_al_y_ref = D.add_ref(pix_al_y)

	pix_nb = create_pixel(cap_angles['nb_x'], cap_angles['nb_y'], cap_layer=layers["nb_base"], abs_layer=layers["nb_base"])
	pix_nb_ref = D.add_ref(pix_nb).move([pix_offset/2., 0])
	pix_nb_x = comp.x_feed_connect(pix_nb_ref, lw=rail_width, feedline_separation=single_material_feedline_sep, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_nb_x_ref = D.add_ref(pix_nb_x)
	pix_nb_y = comp.y_feed_connect(pix_nb_ref, lw=rail_width, feedline_separation=single_material_feedline_sep, feed_lw=feed_pars["lw"], layer=layers["nb_base"])
	pix_nb_y_ref = D.add_ref(pix_nb_y)

	#create feedline
	feed = comp.optical_feedline(feed_pars)
	feed_ref = D.add_ref(feed)

	#create terminal pads
	pad = comp.feedline_pad(feed_pars)
	pad_upper_ref = D.add_ref(pad)
	pad_lower_ref = D.add_ref(pad)
	pad_upper_ref.connect(port='p1', destination=feed_ref.ports['p1'])
	pad_lower_ref.connect(port='p1', destination=feed_ref.ports['p2'])


	#create box outline and stuff
	outline = comp.optical_chip_outline(dev_label, chip_pars)
	outline_ref = D.add_ref(outline)

	#create hole and slot
	hole = geo.circle(radius=397, angle_resolution=2, layer=layers["drill_si_topside"])
	hole_ref = D.add_ref(hole)
	#slot
	slot_left_ref = D.add_ref(hole).movex(9500)
	slot_right_ref = D.add_ref(hole).movex(10500)
	slot = geo.rectangle((992.4, 794), layer=layers["drill_si_topside"])
	slot_ref = D.add_ref(slot).movex(9500).movey(-397)



	return D