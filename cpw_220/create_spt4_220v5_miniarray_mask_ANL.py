#create a wafer of mini arrays

import components as comp
from math import pi
from matplotlib import pyplot as plt
import numpy as np
from phidl import Device
from phidl import geometry as geo
from phidl.quickplotter import quickplot as qp

from create_miniarray_chip import create_miniarray_chip

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


#print(A_tine_lengths)
#print(B_tine_lengths)

chip=[
'-HZHZHZHZH',
'-ININININI',
'-HZHZHZHZH',
'-ININININI',
'-HZHZHZHZH',
'-ININININI',
'-HZHZHZHZH',
'-NNINININI',
'-HZHZHZHZH',
'-GGGGGGGGG'
]

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

#chips

dev_design = 'spt4_220v5'


chip_A1 = create_miniarray_chip(dev_design, "arrA1.1", A_tine_lengths, design=chip)
D.add_ref(chip_A1).movex(-co).movey(co)
chip_B1 = create_miniarray_chip(dev_design,"arrB1.1", B_tine_lengths, design=chip)
D.add_ref(chip_B1).movex(co).movey(-co)

chip_A12 = create_miniarray_chip(dev_design,"arrA1.2", A_tine_lengths, design=chip)
D.add_ref(chip_A12).movex(-co).movey(2*co+13000)
chip_B12 = create_miniarray_chip(dev_design,"arrB1.2", B_tine_lengths, design=chip)
D.add_ref(chip_B12).movex(co).movey(-2*co-13000)

chip_A2 = create_miniarray_chip(dev_design,"arrA2.1", A_sparse_lengths, design=sparse_chip)
D.add_ref(chip_A2).movex(-co).movey(-co)
chip_B2 = create_miniarray_chip(dev_design,"arrB2.2", B_sparse_lengths, design=sparse_chip)
D.add_ref(chip_B2).movex(co).movey(co)

chip_A22 = create_miniarray_chip(dev_design,"arrA2.2", A_sparse_lengths, design=sparse_chip)
D.add_ref(chip_A22).movex(-co).movey(-2*co-13000)
chip_B22 = create_miniarray_chip(dev_design,"arrB2.2", B_sparse_lengths, design=sparse_chip)
D.add_ref(chip_B22).movex(co).movey(2*co+13000)


#outer ring
outer_ring=geo.ring(radius=wafer_pars["outer_radius"]-wafer_pars["outer_ring_thickness"]/2., width=wafer_pars["outer_ring_thickness"], layer=layers["edge_bead"])
outer_ring_ref = D.add_ref(outer_ring)

#alignment markings
align = comp.wafer_alignment_marking()
left_align_ref = D.add_ref(align).movex(-54000)
left_align_ref = D.add_ref(align).movex(54000)


D.write_gds("../../spt4_mask_files/miniarray_test.gds")