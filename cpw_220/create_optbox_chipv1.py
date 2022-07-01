#create miniarray chip but efficiently this time

import components as comp
from math import pi
from matplotlib import pyplot as plt
import numpy as np
from phidl import Path, CrossSection, Device
from phidl import geometry as geo
import phidl.path as pp
from phidl.quickplotter import quickplot as qp

import settings
layers = settings.get_layers()
pars = settings.get_feedline_settings()

feed_width = pars['lw']
cpw_gap = pars['gap']

pix_settings=settings.get_pixel_settings()
pix_radius = pix_settings['full_pixel_radius']


chip_pars=settings.get_chip_settings()


#from cpw_toolkit import connect_feedlines_chip, place_pixels_chip
from create_array_pixel import create_array_pixel
from cpw_toolkit import tile, place_pixels_chip, connect_feedlines_chip

test_design = [
	'NIG',
	'HZH',
	'ING',
	'GGG']


def create_optbox_chip(dev_design, dev_label, cap_sizes, design=test_design):
	array = Device()
	NO_GND = Device()

	x_offset = 3330
	y_offset = 4956

	#opt1 = tile('I', cap_sizes[0], cap_sizes[1])
	print(cap_sizes[0])
	opt1, F1, nognd1  = place_pixels_chip(design, cap_sizes[0])
	C1, N1  = connect_feedlines_chip(F1)
	opt1.add_ref(C1)
	array.add_ref(opt1).movex(6000).movey(6000)
	NO_GND.add_ref(nognd1).movex(6000).movey(6000)
	NO_GND.add_ref(N1).movex(6000).movey(6000)

	opt2, F2, nognd2  = place_pixels_chip(design, cap_sizes[1])
	C2, N2  = connect_feedlines_chip(F2)
	opt2.add_ref(C2)
	array.add_ref(opt2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)
	NO_GND.add_ref(nognd2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)
	NO_GND.add_ref(N2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)


	
	opt3, F3, nognd3  = place_pixels_chip(design, cap_sizes[2])
	C3, N3  = connect_feedlines_chip(F3)
	opt3.add_ref(C3)
	array.add_ref(opt3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)
	NO_GND.add_ref(nognd3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)
	NO_GND.add_ref(N3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)

	
	opt4, F4, nognd4  = place_pixels_chip(design, cap_sizes[3])
	C4, N4  = connect_feedlines_chip(F4)
	opt4.add_ref(C4)
	array.add_ref(opt4).movex(6000).movey(-6000)
	NO_GND.add_ref(nognd4).movex(6000).movey(-6000)
	NO_GND.add_ref(N4).movex(6000).movey(-6000)
	

	#path from cluster 1 to cluster 2

	#rotation offset manual correction
	ro=1.7

	points12=[]
	pre12 = (F1[0][1][0] + 6000, F1[0][1][1] + 6000)
	start12 = (F1[0][0][0] + 6000, F1[0][0][1] + 6000)
	vect12_pre = (start12[0]-pre12[0], start12[1]-pre12[1])

	end12 = (F2[-1][-2][0] - 6000, F2[-1][-2][1] +6000 + ro)
	post12 = (F2[-1][-3][0] - 6000, F2[-1][-3][1] +6000 + ro)
	vect12_post = (end12[0]-post12[0], end12[1]-post12[1])

	points12.append((pre12[0]+0.5*vect12_pre[0], pre12[1]+0.5*vect12_pre[1]))
	points12.append((start12[0]+0.01*vect12_pre[0], start12[1]+0.01*vect12_pre[1]))
	points12.append((start12[0]+0.01*vect12_pre[0]-1000, start12[1]+0.01*vect12_pre[1]))

	points12.append((end12[0]+0.01*vect12_post[0]+1000, end12[1]+0.01*vect12_post[1]))
	points12.append((end12[0]+0.01*vect12_post[0], end12[1]+0.01*vect12_post[1]))
	points12.append((post12[0]+0.5*vect12_post[0], post12[1]+0.5*vect12_post[1]))
	
	path12=comp.polypath_from_points(xypoints = points12, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path12=comp.polypath_from_points(xypoints = points12, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path12)
	NO_GND.add_ref(inv_path12)

	
	#path from cluster 2 to cluster 3
	points23 = []
	pre23 = (F2[0][-3][0] - 6000, F2[0][-3][1] + 6000 + ro)
	start23 = (F2[0][-2][0] - 6000, F2[0][-2][1] + 6000 + ro)
	vect23_pre = (start23[0]-pre23[0], start23[1]-pre23[1])

	end23 = (F3[-1][-2][0] - 6000, F3[-1][-2][1] - 6000 + ro)
	post23 = (F3[-1][-3][0] - 6000, F3[-1][-3][1] - 6000 + ro)
	vect23_post = (end23[0]-post23[0], end23[1]-post23[1])

	points23.append((pre23[0]+0.5*vect23_pre[0], pre23[1]+0.5*vect23_pre[1]))
	points23.append((start23[0]+0.01*vect23_pre[0], start23[1]+0.01*vect23_pre[1]))
	points23.append((start23[0]+0.01*vect23_pre[0]+1000, start23[1]+0.01*vect23_pre[1]))

	points23.append((end23[0]+0.01*vect23_post[0]+1000, end23[1]+0.01*vect23_post[1]))
	points23.append((end23[0]+0.01*vect23_post[0], end23[1]+0.01*vect23_post[1]))
	points23.append((post23[0]+0.5*vect23_post[0], post23[1]+0.5*vect23_post[1]))

	path23=comp.polypath_from_points(xypoints = points23, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path23 = comp.polypath_from_points(xypoints = points23, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path23)
	NO_GND.add_ref(inv_path23)

	

	#path from cluster 3 to cluster 4

	points34=[]
	pre34 = (F3[0][-3][0] - 6000, F3[0][-3][1] - 6000 + ro)
	start34 = (F3[0][-2][0] - 6000, F3[0][-2][1] - 6000 + ro)
	vect34_pre=(start34[0]-pre34[0], start34[1]-pre34[1])

	end34 = (F4[-1][0][0] + 6000, F4[-1][0][1] - 6000)
	post34 = (F4[-1][1][0] + 6000, F4[-1][1][1] - 6000)
	vect34_post = (end34[0]-post34[0], end34[1]-post34[1])

	points34.append((pre34[0]+0.5*vect34_pre[0], pre34[1]+0.5*vect34_pre[1]))
	points34.append((start34[0]+0.01*vect34_pre[0], start34[1]+0.01*vect34_pre[1]))
	points34.append((start34[0]+0.01*vect34_pre[0]+1000, start34[1]+0.01*vect34_pre[1]))

	points34.append((end34[0]+0.01*vect34_post[0]-1000, end34[1]+0.01*vect34_post[1]))
	points34.append((end34[0]+0.01*vect34_post[0], end34[1]+0.01*vect34_post[1]))
	points34.append((post34[0]+0.5*vect34_post[0], post34[1]+0.5*vect34_post[1]))

	path34 = comp.polypath_from_points(xypoints = points34, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path34 = comp.polypath_from_points(xypoints = points34, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path34)
	NO_GND.add_ref(inv_path34)


	#path from cluster 1 to the top bondpad

	points01= []
	pre01 = (F1[-1][1][0] + 6000, F1[-1][1][1] + 6000)
	start01 = (F1[-1][0][0] + 6000, F1[-1][0][1] + 6000)
	vect01_pre=(start01[0]-pre01[0], start01[1]-pre01[1])

	points01.append((pre01[0]+0.5*vect01_pre[0], pre01[1]+0.5*vect01_pre[1]))
	points01.append((start01[0]+0.01*vect01_pre[0], start01[1]+0.01*vect01_pre[1]))
	points01.append((x_offset+1000, start01[1]+0.01*vect01_pre[1]))
	points01.append((x_offset,10000+y_offset))
	points01.append((x_offset,12500+y_offset))

	path01 = comp.polypath_from_points(xypoints = points01, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path01 = comp.polypath_from_points(xypoints = points01, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path01)
	NO_GND.add_ref(inv_path01)


	#path from cluster 4 to the bottom bondpad

	points45= []
	pre45 = (F4[0][1][0] + 6000, F4[0][1][1] - 6000)
	start45 = (F4[0][0][0] + 6000, F4[0][0][1] - 6000)
	vect45_pre=(start45[0]-pre45[0], start45[1]-pre45[1])

	points45.append((pre45[0]+0.5*vect45_pre[0], pre45[1]+0.5*vect45_pre[1]))
	points45.append((start45[0]+0.01*vect45_pre[0], start45[1]+0.01*vect45_pre[1]))
	points45.append((x_offset+1000, start45[1]+0.01*vect45_pre[1]))
	points45.append((x_offset,-10000+y_offset))
	points45.append((x_offset,-12500+y_offset))

	path45 = comp.polypath_from_points(xypoints = points45, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path45 = comp.polypath_from_points(xypoints = points45, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path45)
	NO_GND.add_ref(inv_path45)
	


	#dowel holes
	#create hole and slot
	hole = geo.circle(radius=397, angle_resolution=2, layer=layers["drill_si_topside"])
	array.add_ref(hole).movex(x_offset).movey(y_offset)
	#slot
	array.add_ref(hole).movex(9500).movex(x_offset).movey(y_offset)
	array.add_ref(hole).movex(10500).movex(x_offset).movey(y_offset)
	slot = geo.rectangle((992.4, 794), layer=layers["drill_si_topside"])
	array.add_ref(slot).movex(9500).movey(-397).movex(x_offset).movey(y_offset)

	

	

	#define cross sections of feedline transitions
	X1=CrossSection()
	X1.add(width=30, offset=0, layer=layers["nb_base"], name='feed', ports=(1,2))
	X2=CrossSection()
	X2.add(width=400, offset=0, layer=layers["nb_base"], name='feed', ports=(3,4))
	Xtrans=pp.transition(cross_section1=X1, cross_section2=X2, width_type='linear')
	
	X1_cutout=CrossSection()
	X1_cutout.add(width=80, offset=0, layer=layers["gnd"], name='cutout', ports=(1,2))
	X2_cutout=CrossSection()
	X2_cutout.add(width=1067, offset=0, layer=layers["gnd"], name='cutout', ports=(3,4))
	Xtrans_cutout=pp.transition(cross_section1=X1_cutout, cross_section2=X2_cutout, width_type='linear')

	#top end of feedline
	start_top=(x_offset, y_offset+11000)
	s0 = pp.straight(length=1500)


	P_top_trans=Path()
	P_top_trans.append([s0])
	trans_top=P_top_trans.extrude(Xtrans)
	P_top_trans.append([pp.straight(length=500)])
	trans_cutout_top = P_top_trans.extrude(Xtrans_cutout)
	trans_top_ref = array.add_ref(trans_top).rotate(90).move(start_top)
	trans_cutout_top_ref=NO_GND.add_ref(trans_cutout_top).rotate(90).move(start_top)


	#bottom of feedline
	start_bottom=(x_offset, y_offset-11000)
	s0 = pp.straight(length=1500)

	P_bottom_trans=Path()
	P_bottom_trans.append([s0])
	trans_bottom=P_bottom_trans.extrude(Xtrans)
	P_bottom_trans.append([pp.straight(length=500)])
	trans_cutout_bottom = P_bottom_trans.extrude(Xtrans_cutout)
	trans_bottom_ref = array.add_ref(trans_bottom).rotate(270).move(start_bottom)
	trans_cutout_bottom_ref=NO_GND.add_ref(trans_cutout_bottom).rotate(270).move(start_bottom)


	
	#cpw bridges
	sio2_rect = geo.rectangle(size=(80,160), layer=layers['sio2']).movex(-40)
	bridge = Device()
	strap = geo.rectangle(size=(10,300), layer=layers['bridge']).movex(-5)
	pad = geo.rectangle(size=(112,100), layer=layers['bridge']).movex(-56)
	bridge.add_ref(sio2_rect).movey(75)
	bridge.add_ref(strap)
	bridge.add_ref(pad)
	bridge.add_ref(pad).movey(210)

	#bridge locations
	b12=(x_offset, y_offset+5650)
	array.add_ref(bridge).rotate(-60).move(b12)
	b23 = (x_offset-2000, y_offset)
	array.add_ref(bridge).rotate(90).move(b23)
	b34 = (x_offset, y_offset-6205)
	array.add_ref(bridge).rotate(30).move(b34)

	
	
	
	#create box outline and stuff
	outline = comp.optical_chip_outline(dev_design, dev_label, chip_pars)
	outline_notext = comp.optical_chip_outline_notext(chip_pars)
	array.add_ref(outline_notext).movex(x_offset).movey(y_offset)
	NO_GND.add_ref(outline).movex(x_offset).movey(y_offset)


	#NO_GND.add_ref(outline).movex(-design_offset_x).movey(-design_offset_y)
	side=chip_pars['chip_sidelength']
	GND=geo.rectangle(size=(side, side), layer=layers['gnd']).movex(x_offset-side/2.).movey(y_offset-side/2.)


	gnd_plane = geo.boolean(A=[GND], B=[NO_GND], operation='A-B', layer=layers['gnd'])	
	array.add_ref(gnd_plane)	

	

	return array.movex(-x_offset).movey(-y_offset)


#cap_sizes=[1800,1800,1800,1800,1800,1800,1800,1800]
#cap_sizes=np.multiply(1800, np.ones(1000))
#test = create_optbox_chip('spt4v5', 'test', cap_sizes)
#test.write_gds("../../spt4_mask_files/optbox_test.gds")