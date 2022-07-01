#create a wafer of mini arrays

import components as comp
from math import pi
from matplotlib import pyplot as plt
import numpy as np
from phidl import Device
from phidl import geometry as geo
from phidl.quickplotter import quickplot as qp

from create_miniarray_chip import create_miniarray_chip
from create_optbox_chipv1 import create_optbox_chip

import settings
layers = settings.get_layers()
wafer_pars=settings.get_wafer_settings()

D = Device()

co = wafer_pars['chip_offset']

#Chip A
#mux factor of 500 per feedline
n=27 #kids per bank
#Ax1_27 = [1830+4*i for i in range(n)]
#Ay1_27 = [1630+4*i for i in range(n)]
#Ax28_54 = [1300+3*i for i in range(n)]
#Ay28_54 = [1150+3*i for i in range(n)]
#Ax55_81 = [900+2*i for i in range(n)]
#Ay55_81 = [800+2*i for i in range(n)]
Ax1_27 = [1800+6*i for i in range(n)]
Ay1_27 = [1000+6*i for i in range(n)]
Ax28_54 = [1600+ 6*i for i in range(n)]
Ay28_54 = [800+6*i for i in range(n)]
Ax55_81 = [1400+6*i for i in range(n)]
Ay55_81 = [600+6*i for i in range(n)]
A_banks=[Ax1_27, Ay1_27, Ax28_54, Ay28_54, Ax55_81, Ay55_81]

#Chip B
#mux factor from 500 per feedline to 250 per feedline
#Bx1_27 = [1800+4*i for i in range(n)]
#By1_27 = [1600+4*i for i in range(n)]
#Bx28_54 = [1400+4*i for i in range(n)]
#By28_54 = [1200+4*i for i in range(n)]
#Bx55_81 = [1000+4*i for i in range(n)]
#By55_81 = [800+4*i for i in range(n)]
Bx1_27 = [1800+3*i for i in range(n)]
By1_27 = [1000+3*i for i in range(n)]
Bx28_54 = [1600+3*i for i in range(n)]
By28_54 = [800+3*i for i in range(n)]
Bx55_81 = [1400+3*i for i in range(n)]
By55_81 = [600+3*i for i in range(n)]
B_banks=[Bx1_27, By1_27, Bx28_54, By28_54, Bx55_81, By55_81]


A_sparse_lengths=[]
B_sparse_lengths=[]
for i in range(7):
	A_sparse_lengths.append(Ax1_27[i])
	A_sparse_lengths.append(Ay1_27[i])
	A_sparse_lengths.append(Ax28_54[i])
	A_sparse_lengths.append(Ay28_54[i])
	B_sparse_lengths.append(Bx1_27[i])
	B_sparse_lengths.append(By1_27[i])
	B_sparse_lengths.append(Bx28_54[i])
	B_sparse_lengths.append(By28_54[i])

A_tine_lengths=[]
B_tine_lengths=[]
for i in range(162):
	A_tine_lengths.append(A_banks[i%6][0])
	del(A_banks[i%6][0])
	B_tine_lengths.append(B_banks[i%6][0])
	del(B_banks[i%6][0])


sparse_chip=[
'-GGGGGGGGG',
'-GHGGHGGHG',
'-GGGGGGGGG',
'-GZGGZGGZG',
'-GGGGGGGGG',
'-GNGGNGGNG',
'-GGGGGGGGG',
'-GIGGIGGIG',
'-GGGGGGGGG',
'-GGGGGGGGG'
]

#x1, y1, x2, y2, x3, y3, x0, y0, x4, y4, x5, y5, x6, y6
opt_cap_0 = [800, 1400, 850, 1450, 900, 1500, 600, 1200, 950, 1550, 1000, 1600, 1050, 1650, 5, 5]
opt_cap_1 = [810, 1410, 860, 1460, 910, 1510, 625, 1225, 960, 1560, 1010, 1610, 1060, 1660,5, 5]
opt_cap_2 = [820, 1420, 870, 1470, 920, 1520, 650, 1250, 970, 1570, 1020, 1620, 1070, 1670, 5, 5]
opt_cap_3 = [830, 1430, 880, 1480, 930, 1530, 675, 1275, 980, 1580, 1030, 1630, 1080, 1680, 5, 5]
optical_caps = [opt_cap_0, opt_cap_1, opt_cap_2, opt_cap_3]


dev_design = 'spt4_220v5'

#optically aligned chips
chip_optv11 = create_optbox_chip(dev_design+' (NoBr)', "optv1.1", optical_caps)
D.add_ref(chip_optv11).movex(co).movey(co)
chip_optv12 = create_optbox_chip(dev_design+' (NoBr)', "optv1.2", optical_caps)
D.add_ref(chip_optv11).movex(-co).movey(co)

#standard sparse chips
chip_A21 = create_miniarray_chip(dev_design+' (NoBr)', "arrA2.1", A_sparse_lengths, design=sparse_chip)
D.add_ref(chip_A21).movex(-co).movey(-co)
chip_A22 = create_miniarray_chip(dev_design+' (NoBr)', "arrA2.2", A_sparse_lengths, design=sparse_chip)
D.add_ref(chip_A22).movex(co).movey(-co)


#outer ring
outer_ring=geo.ring(radius=wafer_pars["outer_radius"]-wafer_pars["outer_ring_thickness"]/2., width=wafer_pars["outer_ring_thickness"], layer=layers["edge_bead"])
outer_ring_ref = D.add_ref(outer_ring)

#alignment markings
align = comp.wafer_alignment_marking()
left_align_ref = D.add_ref(align).movex(-44000)
left_align_ref = D.add_ref(align).movex(44000)


D.write_gds("../../spt4_mask_files/optbox_test.gds")