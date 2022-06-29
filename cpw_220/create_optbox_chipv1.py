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

chip=[
'-HZHZHZHZG',
'-GNINININI',
'-HZHZHZHZG',
'-GNINININI',
'-HZHZHZHZG',
'-GNINININI',
'-HZHZHZHZG',
'-GNINININI',
'-HZHZHZHZG',
'-GGGGGGGGG'
]

def create_optbox_chip(dev_design, dev_label, cap_sizes, design=chip):
	array = Device()
	NO_GND = Device()

	x_offset = 3330
	y_offset = 4956

	test_design = [
	'NIG',
	'HZH',
	'ING',
	'GGG']

	#opt1 = tile('I', cap_sizes[0], cap_sizes[1])
	opt1, F1, nognd1  = place_pixels_chip(test_design, cap_sizes)
	C1, N1  = connect_feedlines_chip(F1)
	opt1.add_ref(C1)
	array.add_ref(opt1).movex(6000).movey(6000)
	NO_GND.add_ref(nognd1).movex(6000).movey(6000)
	NO_GND.add_ref(N1).movex(6000).movey(6000)

	opt2, F2, nognd2  = place_pixels_chip(test_design, cap_sizes)
	C2, N2  = connect_feedlines_chip(F2)
	opt2.add_ref(C2)
	array.add_ref(opt2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)
	NO_GND.add_ref(nognd2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)
	NO_GND.add_ref(N2).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(6000)

	opt3, F3, nognd3  = place_pixels_chip(test_design, cap_sizes)
	C3, N3  = connect_feedlines_chip(F3)
	opt3.add_ref(C3)
	array.add_ref(opt3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)
	NO_GND.add_ref(nognd3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)
	NO_GND.add_ref(N3).rotate(180, center=[x_offset,y_offset]).movex(-6000).movey(-6000)

	
	opt4, F4, nognd4  = place_pixels_chip(test_design, cap_sizes)
	C4, N4  = connect_feedlines_chip(F4)
	opt4.add_ref(C4)
	array.add_ref(opt4).movex(6000).movey(-6000)
	NO_GND.add_ref(nognd4).movex(6000).movey(-6000)
	NO_GND.add_ref(N4).movex(6000).movey(-6000)
	

	#path from cluster 1 to cluster 2
	pre12 = (F1[0][1][0] + 6000, F1[0][1][1] + 6000)
	start12 = (F1[0][0][0] + 6000, F1[0][0][1] + 6000)
	point12_1 = (F1[0][0][0] + 5000, F1[0][0][1] + 6000)
	point12_2 = (F2[-1][-2][0] - 5000, F2[-1][-2][1] +6000)
	end12 = (F2[-1][-2][0] - 6000, F2[-1][-2][1] +6000)
	post12 = (F2[-1][-3][0] - 6000, F2[-1][-3][1] +6000)
	points12=[pre12, start12, point12_1, point12_2, end12, post12]
	path12=comp.polypath_from_points(xypoints = points12, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path12=comp.polypath_from_points(xypoints = points12, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path12)
	NO_GND.add_ref(inv_path12)

	#path from cluster 2 to cluster 3
	pre23 = (F2[0][-3][0] - 6000, F2[0][-3][1] + 6000)
	start23 = (F2[0][-2][0] - 6000, F2[0][-2][1] + 6000)
	point23_1 = (F2[0][-2][0] - 5500, F2[0][-2][1] + 6000)
	point23_2 = (F3[-1][-2][0] - 5500, F3[-1][-2][1] - 6000)
	end23 = (F3[-1][-2][0] - 6000, F3[-1][-2][1] - 6000)
	post23 = (F3[-1][-3][0] - 6000, F3[-1][-3][1] - 6000)
	points23 = [pre23, start23, point23_1, point23_2, end23, post23]
	path23=comp.polypath_from_points(xypoints = points23, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path23 = comp.polypath_from_points(xypoints = points23, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path23)
	NO_GND.add_ref(inv_path23)


	#path from cluster 3 to cluster 4
	pre34 = (F3[0][-3][0] - 6000, F3[0][-3][1] - 6000)
	start34 = (F3[0][-2][0] - 6000, F3[0][-2][1] - 6000)
	point34_1 = (F3[0][-2][0] - 5000, F3[0][-2][1] - 6000)
	point34_2 = (F4[-1][0][0] + 5000, F4[-1][0][1] - 6000)
	end34 = (F4[-1][0][0] + 6000, F4[-1][0][1] - 6000)
	post34 = (F4[-1][1][0] + 6000, F4[-1][1][1] - 6000)
	points34 = [pre34, start34, point34_1, point34_2, end34, post34]
	path34 = comp.polypath_from_points(xypoints = points34, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
	inv_path34 = comp.polypath_from_points(xypoints = points34, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
	array.add_ref(path34)
	NO_GND.add_ref(inv_path34)



	#dowel holes
	#create hole and slot
	hole = geo.circle(radius=397, angle_resolution=2, layer=layers["drill_si_topside"])
	array.add_ref(hole).movex(x_offset).movey(y_offset)
	#slot
	array.add_ref(hole).movex(9500).movex(x_offset).movey(y_offset)
	array.add_ref(hole).movex(10500).movex(x_offset).movey(y_offset)
	slot = geo.rectangle((992.4, 794), layer=layers["drill_si_topside"])
	array.add_ref(slot).movex(9500).movey(-397).movex(x_offset).movey(y_offset)

	'''

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
	start=F[-1][0]
	s0 = pp.straight(length=500)
	s1=pp.euler(radius=200, angle=-120)
	s2 = pp.straight(length=1000)
	s3 = pp.euler(radius=500, angle=-90)
	s4 = pp.straight(length=8770)
	s5 = pp.euler(radius=300, angle=90)
	s6 = pp.straight(length=1800)

	P_top=Path()
	P_top.append([s0, s1, s2, s3, s4, s5])
	x1_top=P_top.extrude(X1)
	x1_cutout_top = P_top.extrude(X1_cutout)
	x1_top_ref = D.add_ref(x1_top).rotate(-150).move(start)
	x1_cutout_top_ref=NO_GND.add_ref(x1_cutout_top).rotate(-150).move(start)
	
	P_top_trans=Path()
	P_top_trans.append([s6])
	trans_top=P_top_trans.extrude(Xtrans)
	P_top_trans.append([pp.straight(length=800)])
	trans_cutout_top = P_top_trans.extrude(Xtrans_cutout)
	trans_top_ref = D.add_ref(trans_top)
	trans_cutout_top_ref=NO_GND.add_ref(trans_cutout_top)


	trans_top_ref.connect(3, x1_top_ref.ports[2])
	trans_cutout_top_ref.connect(3, x1_cutout_top_ref.ports[2])



	#bottom of feedline
	start=F[0][0]
	s0 = pp.straight(length=10)
	s1 = pp.euler(radius=200, angle=60)
	s2 = pp.straight(length=100)
	s3 = pp.euler(radius=300, angle=90)
	s4 = pp.straight(length=9700)#length=8770)
	s5 = pp.euler(radius=200, angle=-90)
	s6 = pp.straight(length=1800)


	P_bottom=Path()
	P_bottom.append([s0, s1, s2, s3, s4, s5])
	x1_bottom=P_bottom.extrude(X1)
	x1_cutout_bottom = P_bottom.extrude(X1_cutout)
	x1_bottom_ref = D.add_ref(x1_bottom).rotate(-150).move(start)
	x1_cutout_bottom_ref=NO_GND.add_ref(x1_cutout_bottom).rotate(-150).move(start)

	P_bottom_trans=Path()
	P_bottom_trans.append([s6])
	trans_bottom=P_bottom_trans.extrude(Xtrans)
	P_bottom_trans.append([pp.straight(length=800)])
	trans_cutout_bottom = P_bottom_trans.extrude(Xtrans_cutout)
	trans_bottom_ref = D.add_ref(trans_bottom)
	trans_cutout_bottom_ref=NO_GND.add_ref(trans_cutout_bottom)


	trans_bottom_ref.connect(3, x1_bottom_ref.ports[2])
	trans_cutout_bottom_ref.connect(3, x1_cutout_bottom_ref.ports[2])

	#cpw bridges
	sio2_rect = geo.rectangle(size=(80,160), layer=layers['sio2']).movex(-40)
	bridge = Device()
	strap = geo.rectangle(size=(10,300), layer=layers['bridge']).movex(-5)
	pad = geo.rectangle(size=(112,100), layer=layers['bridge']).movex(-56)
	bridge.add_ref(sio2_rect).movey(75)
	bridge.add_ref(strap)
	bridge.add_ref(pad)
	bridge.add_ref(pad).movey(210)
	D.add_ref(bridge).movex(4050).movey(20884)
	D.add_ref(bridge).movex(4050).movey(20884-20294)
	D.add_ref(bridge).movex(10050).movey(20884)
	D.add_ref(bridge).movex(10050).movey(20884-20294)

	'''
	
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
cap_sizes=np.multiply(1800, np.ones(1000))
test = create_optbox_chip('spt4v5', 'test', cap_sizes)
test.write_gds("../../spt4_mask_files/optbox_test.gds")