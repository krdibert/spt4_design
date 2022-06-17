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


from cpw_toolkit import connect_feedlines_chip, place_pixels_chip

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

def create_miniarray_chip(dev_design, dev_label, cap_sizes, design=chip):
	array = Device()
	D, F, NO_GND = place_pixels_chip(design, cap_sizes)
	C,N = connect_feedlines_chip(F)
	D.add_ref(C)
	NO_GND.add_ref(N)

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


	#create box outline and stuff
	outline = comp.optical_chip_outline(dev_design, dev_label, chip_pars)
	outline_notext = comp.optical_chip_outline_notext(chip_pars)
	array.add_ref(outline_notext)

	design_offset_x=-13000
	design_offset_y=-11000
	NO_GND.add_ref(outline).movex(-design_offset_x).movey(-design_offset_y)
	side=chip_pars['chip_sidelength']
	GND=geo.rectangle(size=(side, side), layer=layers['gnd']).movex(0).movey(-2000)

	gnd_plane = geo.boolean(A=[GND], B=[NO_GND], operation='A-B', layer=layers['gnd'])	
	D.add_ref(gnd_plane)	
	array.add_ref(D).movex(design_offset_x).movey(design_offset_y)

	return array