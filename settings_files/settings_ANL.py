#ANL 6in wafer version of SPT4_220_v3

#IDC SIZES ARE AT THE END OF THE FILE



#LAYERS

layers={
	"align" : 0,
	"al_base" : 1,
	"nb_base" : 2,
	"drill_si_backside" : 3,
	"drill_si_topside" : 4,
	"edge_bead" : 5,
	"trim"	: 6,
	"tabs": 7,
	"liftoff_a": 8,
	"liftoff_b": 9
	
}

def get_layers():
	return layers

#----------------- WAFER SETTINGS ------------------------

wafer_pars={
	"outer_radius":105000/2. * 1.5,
	"outer_ring_thickness":5000,
	"chip_offset" : 16000}

def get_wafer_settings():
	return wafer_pars

#----------------- PIXEL SETTINGS -------------------------

#resonator capacitors
x_rcap_pars = {
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 43,
	"rail_width"        : 6.,
	'rail_extend_in'    : 50.,
	'rail_extend_out'   : 10.,
	'theta'             : None,
	'outer_radius'      : 1050,
	'start_angle'       : None,
	"layer"             : None}

y_rcap_pars = {
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 32,
	"rail_width"        : 6.,
	'rail_extend_in'    : 50.,
	'rail_extend_out'   : 10.,
	'theta'             : None,
	'outer_radius'      : 1050,
	'start_angle'       : None,
	"layer"             : None}


#coupling capacitors
ccap_pars = {"tine_length" : 40.,
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 4,
	"rail_width"        : 6.,
	'rail_extend_top'   : 0.,
	'rail_extend_bottom': 0.,
	"layer"             : None}


#absorbers
def x_function(u, start_length):
	if u > 61:
		return start_length + (u-61)**2/150.
	elif u < 61:
		return start_length + (61-u)**2/150.
	else: return start_length


def y_function(u, start_length):
	return start_length + (u)**2/100.

#absorbers
def x_220(u, start_length):
	return start_length


def y_220(u, start_length):
	return start_length


x_abs_pars = {
		"num_unit"	: 125,
		"lw"		: 2,
		"start_length"	: 16,
		"center_spacing" : 4,
		"function"	: x_220,
		"layer"		: None}

y_abs_pars = {
		"num_unit"	: 60,
		"lw"		: 2,
		"start_length"	: 16,
		"center_spacing" : 4,
		"function"	: y_220,
		"layer"		: None}


pixel_settings = {
		"full_pixel_radius": 1150, #pixel radius in micron (2.3mm here)
		"membrane_radius": 1000,
		"x_rcap_pars"	: x_rcap_pars,
		"y_rcap_pars"	: y_rcap_pars,
		"x_abs_pars"	: x_abs_pars,
		"y_abs_pars"	: y_abs_pars,
		"ccap_pars"		: ccap_pars}

def get_pixel_settings():
	return pixel_settings

#---------------------- OPTICAL CHIP -----------------------

opt_chip_pars={
	'chip_sidelength' : 26000,
	'outline_width'	: 100,
	'outline_offset' : 500,
	'text_layer'	: layers["nb_base"],
	'line_layer' : layers['drill_si_topside']}

opt_feed_pars={
	"lw"	: 80,
	"pix_radius"	: 1150,
	"pix_offset"	: 6000,
	"feedline_separation"	:1000,
	"pad_sidelength" : 450,
	"trans_length"	: 1450,
	"layer"	: layers["nb_base"]}

optical_chip_settings = {
	"chip_pars"	: opt_chip_pars,
	"feed_pars"	: opt_feed_pars,
	"rail_width": ccap_pars["rail_width"]}

def get_optical_chip_settings():
	return optical_chip_settings

#---------------------------- DARK CHIP ------------------------------

drk_chip_pars={
	'chip_sidelength' : 26000,
	'chip_sidewidth' : 11000,
	'outline_width'	: 100,
	'outline_offset' : 500,
	'text_layer'	: layers["nb_base"],
	'line_layer' : layers['drill_si_topside']}

drk_feed_pars={
	"lw"	: 80,
	"pix_radius"	: 1150,
	"pix_spacing"	: 4000,
	"feedline_separation"	:800,
	"pad_sidelength" : 450,
	"trans_length"	: 1450,
	"layer"	: layers["nb_base"]}

dark_chip_settings = {
	"chip_pars"	: drk_chip_pars,
	"feed_pars"	: drk_feed_pars,
	"rail_width": ccap_pars["rail_width"]}

def get_dark_chip_settings():
	return dark_chip_settings


#---------- TEST STRUCTURES --------------------
test_pars_al={
	'pad_sidelength':500,
	'trans_length':500,
	'lw':10,
	'length':3000,
	'layer':layers["al_base"],
	'box_layer': layers["nb_base"],
	'boxw':62,
	'boxh': 100}

test_pars_nb={
	'pad_sidelength':500,
	'trans_length':500,
	'lw':10,
	'length':3000,
	'layer':layers["nb_base"],
	'box_layer': None,
	'boxw':62,
	'boxh': 100}

test_structure_settings={
	"test_pars_al"	: test_pars_al,
	"test_pars_nb"	: test_pars_nb
}

def get_test_structure_settings():
	return test_structure_settings


opt_tine_lengths = {
	'p1_x' : 968,
	'p1_y' : 830,
	'p2_x' : 953,
	'p2_y' : 816,
	'p3_x' : 936,
	'p3_y' : 800,
	'p4_x' : 921,
	'p4_y' : 786,
	'd1_x' : 702,
	'd1_y' : 587,
	'd2_x' : 692,
	'd2_y' : 578,
	'al_x' : 675,
	'al_y' : 529,
	'nb_x' : 1168,
	'nb_y' : 887
}


dark_tine_lengths={
	'd1_x' : 968,
	'd1_y' : 830,
	'd2_x' : 953,
	'd2_y' : 816,
	'd3_x' : 936,
	'd3_y' : 800,
	'd4_x' : 702,
	'd4_y' : 587,
	'd5_x' : 692,
	'd5_y' : 578

}

dark_tine_spaced_lengths={
	'd1_x' : 968*1.3,
	'd1_y' : 830*1.3,
	'd2_x' : 953*1.3,
	'd2_y' : 816*1.3,
	'd3_x' : 936*1.3,
	'd3_y' : 800*1.3,
	'd4_x' : 702*1.3,
	'd4_y' : 587*1.3,
	'd5_x' : 692*1.3,
	'd5_y' : 578*1.3

}

idc_settings = {
	"opt_tine_lengths"	: opt_tine_lengths,
	"dark_tine_lengths"	: dark_tine_lengths,
	"dark_tine_spaced_lengths"	: dark_tine_spaced_lengths
}


def get_idc_settings():
	return idc_settings
