
import components as comp
from math import pi
from matplotlib import pyplot as plt
from phidl import Device
from phidl import geometry as geo
from phidl.quickplotter import quickplot as qp
from pys4fab.core import tools
# -----------------------------------------------------------------------------
#layers

import settings
layers = settings.get_layers()

# -----------------------------------------------------------------------------
from create_optical_chip import create_optical_chip
from create_dark_chip import create_dark_chip

wafer_pars = settings.get_wafer_settings()

idc_settings = settings.get_idc_settings()
opt_tine_lengths = idc_settings["opt_tine_lengths"]
dark_tine_lengths = idc_settings["dark_tine_lengths"]
dark_tine_spaced_lengths = idc_settings["dark_tine_spaced_lengths"]

test_structure_settings = settings.get_test_structure_settings()
test_pars_al = test_structure_settings["test_pars_al"]
test_pars_nb = test_structure_settings["test_pars_nb"]


D = Device()

co = wafer_pars["chip_offset"]

#optical chips
optical_chip_A = create_optical_chip("optA", opt_tine_lengths)
optical_chip_A_ref = D.add_ref(optical_chip_A).movex(-co).movey(co)

optical_chip_B = create_optical_chip("optB", opt_tine_lengths)
optical_chip_B_ref = D.add_ref(optical_chip_B).movex(-co).movey(-co)

#dark chips
dark_chip_A = create_dark_chip("drkA", dark_tine_lengths)
dark_chip_ref_A = D.add_ref(dark_chip_A).rotate(90).movex(co/2.).movey(co)

dark_chip_B = create_dark_chip("drkB", dark_tine_lengths)
dark_chip_ref_B = D.add_ref(dark_chip_B).rotate(90).movex(3*co/2.).movey(co)

#double spaced dark chips
dark_chip_C = create_dark_chip("drkC (DS)", dark_tine_spaced_lengths, double_space=True)
dark_chip_ref_C = D.add_ref(dark_chip_C).rotate(90).movex(co/2.).movey(-co)

dark_chip_D = create_dark_chip("drkD (DS)", dark_tine_spaced_lengths, double_space=True)
dark_chip_ref_D = D.add_ref(dark_chip_D).rotate(90).movex(3*co/2.).movey(-co)


#outer ring
outer_ring=geo.ring(radius=wafer_pars["outer_radius"]-wafer_pars["outer_ring_thickness"]/2., width=wafer_pars["outer_ring_thickness"], layer=layers["edge_bead"])
outer_ring_ref = D.add_ref(outer_ring)

#alignment markings
align = comp.wafer_alignment_marking()
left_align_ref = D.add_ref(align).movex(-44000)
left_align_ref = D.add_ref(align).movex(44000)

#test structures at top of wafer
test_al = comp.test_structure(test_pars_al, label="AL ONLY", include_boxes=False)
test_al_nb = comp.test_structure(test_pars_al, label="AL-NB", include_boxes=True)
test_nb = comp.test_structure(test_pars_nb, label="NB ONLY", include_boxes=False)
test_al_ref=D.add_ref(test_al).movey(40000).movex(-10000)
test_al_nb_ref_1=D.add_ref(test_al_nb).movey(37000).movex(-10000)
test_al_nb_ref_2=D.add_ref(test_al_nb).movey(34000).movex(-10000)
test_nb_ref=D.add_ref(test_nb).movey(34000).movex(-20000)

test_device=Device()
test2_al = comp.test_structure_2(pad_layer=layers["al_base"], line_layer=layers["al_base"], label="AL ONLY")
test2_al_nb = comp.test_structure_2(pad_layer=layers["al_base"], line_layer=layers["nb_base"], label="AL-NB")
test2_gap = comp.test_structure_2(pad_layer=layers["al_base"], line_layer=None, label="AL GAP", line=False)
test2_nb = comp.test_structure_2(pad_layer=layers["nb_base"], line_layer=layers["nb_base"], label="NB ONLY")
test2_al_ref=test_device.add_ref(test2_al).movey(40000).movex(10000)
test2_al_nb_ref=test_device.add_ref(test2_al_nb).movey(37000).movex(10000)
test2_gap=test_device.add_ref(test2_gap).movey(34000).movex(10000)
test2_nb_ref=test_device.add_ref(test2_nb).movey(34000).movex(20000)
test_dev_1 = D.add_ref(test_device)
test_dev_2 = D.add_ref(test_device).rotate(90)
test_dev_3 = D.add_ref(test_device).rotate(180)
test_dev_4 = D.add_ref(test_device).rotate(270)



qp(D)
plt.xlabel('microns')
plt.ylabel('microns')
plt.show()

#D.write_gds("spt4_mask_220_v3_ANL_liftoff.gds")

