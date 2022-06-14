

#SPT4_TLS

#IDC SIZES ARE AT THE END OF THE FILE



#LAYERS

layers={
	"align" : 0,
	"al_base" : 1,
	"nb_base" : 2,
	"drill_si_backside" : 3,
	"drill_si_topside" : 4,
	"edge_bead" : 5,
	"sio2"	: 6,
	"gnd": 7,
	"bridge": 8
	
}

def get_layers():
	return layers

#----------------- WAFER SETTINGS ------------------------

wafer_pars={
	"outer_radius":105000/2.,
	"outer_ring_thickness":5000,
	"chip_offset" : 16000}

#ANL wafer pars
#wafer_pars={
#	"outer_radius":150000/2.,
#	"outer_ring_thickness":5000,
#	"chip_offset" : 16000}

def get_wafer_settings():
	return wafer_pars

#----------------- PIXEL SETTINGS -------------------------

#BASELINE SETTINGS

#resonator capacitors
x_rcap_pars = {
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 31,
	"rail_width"        : 6.,
	'rail_extend_in'    : 0.,
	'rail_extend_out'   : 0.,
	'theta'             : None,
	'outer_radius'      : 925,
	'start_angle'       : None,
	"layer"             : None}

y_rcap_pars = {
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 31,
	"rail_width"        : 6.,
	'rail_extend_in'    : 0.,
	'rail_extend_out'   : 0.,
	'theta'             : None,
	'outer_radius'      : 925,
	'start_angle'       : None,
	"layer"             : None}


#coupling capacitors
ccap_pars = {"tine_length" : 200.,
	"tine_spacing"      : 4.,
	"tine_linewidth"    : 4.,
	"numtines"          : 4,
	"rail_width"        : 6.,
	'rail_extend_top'   : 150.,
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
		"membrane_radius": 800,
		"x_rcap_pars"	: x_rcap_pars,
		"y_rcap_pars"	: y_rcap_pars,
		"x_abs_pars"	: x_abs_pars,
		"y_abs_pars"	: y_abs_pars,
		"ccap_pars"		: ccap_pars}

#default pixel
def get_pixel_settings():
	return pixel_settings


#---------------------------- FEEDLINE GENERAL SETTINGS ------------------------------

feed_pars={
	"lw"	: 30,
	"gap"	: 25,
	"pix_radius"	: pixel_settings["full_pixel_radius"],
	"pix_spacing"	: 4000,
	"feedline_separation"	:1000,
	"pad_sidelength" : 400,
	"trans_length"	: 1500,
	"layer"	: layers["nb_base"]}


def get_feedline_settings():
	return feed_pars


opt_chip_pars={
	'chip_sidelength' : 26000,
	'outline_width'	: 100,
	'outline_offset' : 500,
	'text_layer'	: layers["nb_base"],
	'line_layer' : layers['drill_si_topside']}

def get_chip_settings():
	return opt_chip_pars
#-------------------------------------- IDC TINE LENGTHS --------------------------------------------
A_tine_lengths={
	'd1_x' :1600 ,
	'd1_y' :500 ,
	'd2_x' :1600,
	'd2_y' :500,
	'd3_x' :1600 ,
	'd3_y' :500 ,
	'd4_x' :1600 ,
	'd4_y' :500 ,
	'd5_x' :1600 ,
	'd5_y' :500 

}

B_tine_lengths={
	'd1_x' :1200 ,
	'd1_y' :400 ,
	'd2_x' :1200 ,
	'd2_y' :400 ,
	'd3_x' :1200 ,
	'd3_y' :400 ,
	'd4_x' :1200 ,
	'd4_y' :400 ,
	'd5_x' :1200 ,
	'd5_y' :400 

}

C_tine_lengths={
	'd1_x' :800 ,
	'd1_y' :400 ,
	'd2_x' :800 ,
	'd2_y' :400 ,
	'd3_x' :800 ,
	'd3_y' :400 ,
	'd4_x' :800 ,
	'd4_y' :400 ,
	'd5_x' :800 ,
	'd5_y' :400 

}

D_tine_lengths={
	'd1_x' :400 ,
	'd1_y' :400 ,
	'd2_x' :600 ,
	'd2_y' :600 ,
	'd3_x' :800 ,
	'd3_y' :800 ,
	'd4_x' :1200 ,
	'd4_y' :1200 ,
	'd5_x' :1600 ,
	'd5_y' :1600 

}



idc_settings = {
	"A_tine_lengths"	: A_tine_lengths,
	"B_tine_lengths"	: B_tine_lengths,
	"C_tine_lengths"	: C_tine_lengths,
	"D_tine_lengths"	: D_tine_lengths,
}


def get_idc_settings():
	return idc_settings
