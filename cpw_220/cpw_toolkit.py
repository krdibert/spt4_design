#toolkid for making cpw arrays

import components as comp
from math import pi
from matplotlib import pyplot as plt
import numpy as np
from phidl import Path, CrossSection, Device
from phidl import geometry as geo
import phidl.path as pp
from phidl.quickplotter import quickplot as qp

#from pys4fab.core import tools
from create_array_pixel import create_array_pixel as create_pixel

import settings
layers = settings.get_layers()
pars = settings.get_feedline_settings()

feed_width = pars['lw']
cpw_gap = pars['gap']

pix_settings=settings.get_pixel_settings()
pix_radius = pix_settings['full_pixel_radius']


chip_pars=settings.get_chip_settings()

cpw_gnd_wall_real=40
cpw_gnd_wall = (cpw_gnd_wall_real-30)*2. + 30
coupling_sep=20.
coupling_length = 500 #20 um bend radius


circle_sep=feed_width+2*cpw_gap
tile_sidelength = 2*pix_radius-circle_sep

factor=np.sqrt(3)/2.#np.sin(60*np.pi/180.)


#create a set of array tiles
def tile(s, capsize_x, capsize_y):

	T = Device()
	#if True: return T #use for debugging array placement

	if s=='-' or s=='G': return T

	#4 rotations
	rotations = {'I':90, 'N':135, 'H':0, 'Z':45, }
	rot=rotations[s]+60

	pix = create_pixel(capsize_x, capsize_y, orientation=s, cap_layer=layers['nb_base'], abs_layer=layers["al_base"]).rotate(rot)

	#draw the coupling and ground lines

	#offsets for placing coupling strips
	coupling_dist = coupling_sep+3
	wire_step = 30
	xc_offset = coupling_dist*np.sin(np.pi/6.) #radially
	yc_offset = coupling_dist*np.cos(np.pi/6.)
	xc_coord = coupling_length*np.cos(np.pi/6.) #tangentially
	yc_coord = coupling_length*np.sin(np.pi/6.)
	xc_step = wire_step*np.sin(np.pi/6.) #radially
	yc_step = wire_step*np.cos(np.pi/6.)

	gnd_offset = pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall

	#points at which paths end
	x_offset = pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall-40*np.cos(np.pi/6.) - xc_offset
	y_offset = factor*tile_sidelength/3.-circle_sep/2.+40*np.sin(np.pi/6.) - yc_offset
	LU = (-x_offset , y_offset)
	LB = (-x_offset , -y_offset)
	RU = (x_offset , y_offset)
	RB = (x_offset , -y_offset)

	def get_coupling_point(port):
		G = False
		Overlap = False
		x = port.midpoint[0]
		y = port.midpoint[1]

		cp = [(x,y)]
		angle = np.arctan2(y,x)*180/np.pi
		if angle < 0: angle+=360
		if angle>30 and angle<90:
			if angle>85: Overlap=True
			if angle<35: G=True
			p1 = RU
			p2 = (RU[0]-xc_coord, RU[1]+yc_coord)
		elif angle>90 and angle<150:
			if angle<95: Overlap=True
			if angle>145: G=True
			p1 = LU
			p2 = (LU[0]+xc_coord, LU[1]+yc_coord)
		elif angle>150 and angle<210:
			#gnd
			G=True
			p1=(-gnd_offset, LU[1])
			p2=(-gnd_offset, LB[1])
		elif angle>210 and angle<270 :
			if angle>265: Overlap=True
			if angle<215: G=True
			p1 = LB
			p2 = (LB[0]+xc_coord, LB[1]-yc_coord)
		elif angle>270 and angle<330:
			if angle<275: Overlap=True
			if angle>325: G=True
			p1 = RB
			p2 = (RB[0]-xc_coord, RB[1]-yc_coord)
		elif angle<30 or angle>330:
			#gnd
			G = True
			p1=(gnd_offset, RU[1])
			p2=(gnd_offset, RB[1])
		else: return None

		#intersection with right place
		z = comp.calc_line_intersect(port.midpoint, (0,0), p1, p2)

		if Overlap:
			cp.append((x+(z[0]-x)/2., y+(z[1]-y)/2.))
		else: cp.append(z)

		#choose which way to run the line
		dist = np.array([p1[0]-z[0], p1[1]-z[1]])
		hat = dist/np.linalg.norm(dist)
		if np.linalg.norm(dist) < coupling_length: hat*=-1
		
		if Overlap:
			shift = 200*hat
			cp.append((z[0] + shift[0], z[1]+shift[1]))

		line = hat*coupling_length

		if Overlap: end = (z[0]+shift[0]+line[0], z[1]+shift[1]+line[1])
		else: end = (z[0] + line[0], z[1] + line[1])
		cp.append(end)

		to_gnd_hat= np.array([z[0]-x, z[1]-y])
		norm = np.linalg.norm(to_gnd_hat)
		to_gnd_hat = to_gnd_hat/norm
		to_gnd = to_gnd_hat*(norm+coupling_dist+5)
		gend = (x+to_gnd[0], y+to_gnd[1])


		#end = (z[0] + xc_coord, z[1] + yc_coord)

		return cp, gend, G

	#decide which will be coupled and which will be ground
	cpx1, gendx1, Gx1 = get_coupling_point(pix.ports['x1'])
	cpx3, gendx3, Gx3 = get_coupling_point(pix.ports['x3'])
	cpy1, gendy1, Gy1 = get_coupling_point(pix.ports['y1'])
	cpy3, gendy3, Gy3 = get_coupling_point(pix.ports['y3'])

	if not Gx1:
		x_coupling_path=cpx1
		x_gnd_path=[pix.ports['x3'].midpoint, gendx3]
	else: 
		if Gx3: print('COUPLING WARNING: '+s)
		x_coupling_path=cpx3
		x_gnd_path=[pix.ports['x1'].midpoint, gendx1]

	if not Gy1:
		y_coupling_path=cpy1
		y_gnd_path=[pix.ports['y3'].midpoint, gendy3]
	else: 
		if Gy3: print('COUPLING WARNING: '+ s)
		y_coupling_path=cpy3
		y_gnd_path=[pix.ports['y1'].midpoint, gendy1]



	X_COUP=comp.polypath_from_points(xypoints = x_coupling_path, lw = 6, layer = layers['nb_base'], corners="circular bend", bend_radius=10)#"smooth")
	T.add_ref(X_COUP)
	Y_COUP=comp.polypath_from_points(xypoints = y_coupling_path, lw = 6, layer = layers['nb_base'], corners="circular bend", bend_radius=10)#"smooth")
	T.add_ref(Y_COUP)
	X_GND=comp.polypath_from_points(xypoints = x_gnd_path, lw = 6, layer = layers['nb_base'], corners="smooth")
	T.add_ref(X_GND)
	Y_GND=comp.polypath_from_points(xypoints = y_gnd_path, lw = 6, layer = layers['nb_base'], corners="smooth")
	T.add_ref(Y_GND)

	pix_ref = T.add_ref(pix)

	return T


#right now, the cap sizes just change by 10um
def place_pixels(design, cap_sizes):

	count=0
	D = Device()

	#GND=Device()
	NO_GND=Device()

	if 'G' in design[-1]: row_polarity=-1
	else: row_polarity=1

	feedline_array=[]
	points=[]
	
	offset = tile_sidelength/2.

	x=tile_sidelength/2.
	if row_polarity<0: 
			x+=offset
	y=tile_sidelength/2.

	fx = 0
	fy = tile_sidelength
	#if row_polarity<0: 
	#		fy+=np.sin(60*np.pi/180.)*tile_sidelength

	bottom_row=True

	#left to right, top to bottom
	for line in list(reversed(design)):

		fx=x-tile_sidelength/2.

		for i in range(len(line)):

			char=line[i]

			#place the tile
			t=tile(char, cap_sizes[count*2], cap_sizes[count*2+1])
			if char in ['H', 'Z', 'N', 'I']: count+=1
			D.add_ref(t).move([x,y])

			#add feedline points
			#over
			if char in ['H', 'Z', 'N', 'I', 'G']:
				points.append((fx, fy-tile_sidelength/2. + factor*tile_sidelength/3.))
				points.append((fx+tile_sidelength/2., fy-tile_sidelength/2 + factor*2*tile_sidelength/3.))
				points.append((fx+tile_sidelength, fy-tile_sidelength/2. + factor*tile_sidelength/3.))

				#cpw bridges
				sio2_rect = geo.rectangle(size=(160,160), layer=layers['sio2']).movex(-80)
				D.add_ref(sio2_rect).movex(fx+tile_sidelength/2.).movey(fy-tile_sidelength/2 + factor*2*tile_sidelength/3.-100)
				bridge = geo.rectangle(size=(120,360), layer=layers['bridge']).movex(-60).movey(-180)
				D.add_ref(bridge).movex(fx+tile_sidelength/2.).movey(fy-tile_sidelength/2 + factor*2*tile_sidelength/3.)
				if line[i-1] != '-':
					D.add_ref(sio2_rect).movex(fx).movey(fy-tile_sidelength/2. + factor*tile_sidelength/3.-50)
					D.add_ref(bridge).movex(fx).movey(fy-tile_sidelength/2. + factor*tile_sidelength/3.)


				if char=='G':
					x+=tile_sidelength
					fx+=tile_sidelength 
					continue

				#gnd plane and cutout
				#NOTE: make this into an irregular hexagon (two triangles and a rectangle)
				triangle_fx_offset = pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall
				triangle_lo_fy_offset = -tile_sidelength/2. + factor*tile_sidelength/3.-circle_sep/2.
				#triangle_hi_fy_offset = -tile_sidelength/2 + factor*2*tile_sidelength/3.-circle_sep
				triangle_hi_fy_offset = triangle_lo_fy_offset + triangle_fx_offset*np.tan(np.pi/6.)
				bevel_1=[(fx+tile_sidelength/2.-120*np.cos(np.pi/6.), fy+triangle_hi_fy_offset-120*np.sin(np.pi/6.)), (fx+tile_sidelength/2.+120*np.cos(np.pi/6.), fy+triangle_hi_fy_offset-120*np.sin(np.pi/6.))]
				bevel_2 = [(bevel_1[0][0]+40, bevel_1[0][1]-40),(bevel_1[1][0]-40, bevel_1[1][1]-40)]
				triangle_points=[(fx+tile_sidelength/2. - triangle_fx_offset, fy+triangle_lo_fy_offset), bevel_1[0], bevel_2[0], bevel_2[1], bevel_1[1], (fx+tile_sidelength/2.+triangle_fx_offset, fy+triangle_lo_fy_offset)]
				#no_gnd=geo.circle(radius=pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall, layer=layers["gnd"]).movex(x).movey(y)
				rect_cutout_width = 2*(pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall)
				rect_cutout_height = tile_sidelength + 2*triangle_lo_fy_offset
				no_gnd_rect = geo.rectangle(size=(rect_cutout_width, rect_cutout_height), layer=layers['gnd']).movex(x-rect_cutout_width/2.).movey(y-rect_cutout_height/2.)
				NO_GND.add_ref(no_gnd_rect)
				triangle=Device()
				triangle.add_polygon(triangle_points, layer=layers['gnd'])
				NO_GND.add_ref(triangle)
				NO_GND.add_ref(triangle).mirror(p1=[fx, fy-tile_sidelength/2.], p2=[fx+tile_sidelength, fy-tile_sidelength/2.])
				#gnd_blank = geo.rectangle(size=(tile_sidelength*1.2, tile_sidelength*1.2), layer=layers["gnd"]).movex(fx).movey(fy-tile_sidelength)
				#GND.add_ref(gnd_blank)

				
			x+=tile_sidelength
			fx+=tile_sidelength

		#increment tile info
		x=tile_sidelength/2.
		if row_polarity>0: 
			x+=offset
		y+=factor*tile_sidelength

		#make feedline
		print(count)
		if bottom_row:
			#print('Bottom')
			points=points[1:]
			bottom_row=False
		path=comp.polypath_from_points(xypoints = points, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=100)
		inv_cpw=comp.polypath_from_points(xypoints = points, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=100)
		D.add_ref(path)
		NO_GND.add_ref(inv_cpw)
		feedline_array.append(points)
		points=[]
		fy+=factor*tile_sidelength

		row_polarity*= -1

	#D.add_ref(NO_GND)
	#gnd_plane = geo.boolean(A=[GND], B=[NO_GND], operation='A-B', layer=layers['gnd'])	
	#D.add_ref(gnd_plane)

	print('Total pixel count: ' + str(count))

	return D, feedline_array, NO_GND



triangle=[
'--------------Z',
'--------------IN',
'-------------HZH',
'-------------NINI',
'------------ZHZHZ',
'------------INININ',
'-----------HZHZHZH',
'-----------NINININI',
'----------ZHZHZHZHZ',
'----------INININININ',
'---------HZHZHZHZHZH',
'---------NINININININI',
'--------ZHZHZHZHZHZHZ',
'--------INININININININ',
'-------HZHZHZHZHZHZHZH',
'-------NINININININININI',
'------ZHZHZHZHZHZHZHZHZ',
'------INININININININININ',
'-----HZHZHZHZHZHZHZHZHZH',
'-----NINININININININININI',
'----ZHZHZHZHZHZHZHZHZHZHZ',
'----INININININININININININ',
'---HZHZHZHZHZHZHZHZHZHZHZH',
'---NINININININININININININI',
'--ZHZHZHZHZHZHZHZHZHZHZHZHZ',
'--INININININININININININININ',
'-HZHZHZHZHZHZHZHZHZHZHZHZHZH',
'-NINININININININININININININI',
'GGGGGGGGGGGGGGGGGGGGGGGGGGGG']


def connect_feedlines_tri(F):
	C = Device(name='C')
	N=Device()

	top_port = None

	i=0
	pointer = 0
	while i < len(F):


		if i==len(F)-1: 
				start=F[i][-1]
				prev=F[i][-2]
				connect=[(prev[0]+ (start[0]-prev[0])/2., prev[1] + (start[1]-prev[1])/2.)]
				connect.append(start)
				connect.append((start[0]+ (start[0]-prev[0])/15., start[1] + (start[1]-prev[1])/15.))
				connect.append((start[0]+ (start[0]-prev[0])/15., start[1] - (start[1]-prev[1])/2.))
				connect.append((prev[0], prev[1]- (start[1]-prev[1])/2.))
				top_port=connect[-1]
				i+=1


		elif pointer == 0:
		#right side


			start=F[i][-1]
			prev=F[i][-2]
			end=F[i+1][-1]
			nex=F[i+1][-2]
			
			connect=[(prev[0]+ (start[0]-prev[0])/2., prev[1] + (start[1]-prev[1])/2.)]
			connect.append(start)
			if i==0: connect.append((start[0]+tile_sidelength/2., start[1]+ factor*tile_sidelength/3.))
			else:
				connect.append((start[0]+ (start[0]-prev[0])/15., start[1] + (start[1]-prev[1])/15.))
				connect.append((start[0]+ (start[0]-prev[0])/15., start[1] - (start[1]-prev[1])/2.))
				connect.append((end[0]- (nex[0]-end[0])/10., end[1] - (nex[1]-end[1])*1.5))
				connect.append((end[0]- (nex[0]-end[0])/10., end[1] - (nex[1]-end[1])/10.))
			connect.append(end)
			connect.append((end[0]+ (nex[0]-end[0])/2., end[1] + (nex[1]-end[1])/2.))
			i+=1

		elif pointer == 1:
		#left side
			start=F[i][0]
			end=F[i+1][0]
			prev=F[i][1]
			nex=F[i+1][1]
			connect=[(prev[0]+ (start[0]-prev[0])/2., prev[1] + (start[1]-prev[1])/2.)]
			connect.append(start)
			connect.append((start[0]+ (start[0]-prev[0])/15., start[1] + (start[1]-prev[1])/15.))
			connect.append((start[0]+ (start[0]-prev[0])/15., start[1] - (start[1]-prev[1])/2.))
			connect.append((end[0]- (nex[0]-end[0])/10., end[1] - (nex[1]-end[1])*1.5))
			connect.append((end[0]- (nex[0]-end[0])/10., end[1] - (nex[1]-end[1])/10.))
			connect.append(end)
			connect.append((end[0]+ (nex[0]-end[0])/2., end[1] + (nex[1]-end[1])/2.))
			i+=1

		else: pass

		pointer+=1
		pointer=pointer%2
		path = comp.polypath_from_points(xypoints=connect, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=50)
		C.add_ref(path)
		Npath = comp.polypath_from_points(xypoints=connect, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=50)
		N.add_ref(Npath)


	#C.add_port(name='p1', midpoint=F[-1][0], orientation=0)
	#C.add_port(name='p2', midpoint=F[0][0], orientation=0)

	#feedline transitions to bondpads
	#define cross sections of feedline transitions
	X1=CrossSection()
	X1.add(width=30, offset=0, layer=layers["nb_base"], name='feed')
	X2=CrossSection()
	X2.add(width=400, offset=0, layer=layers["nb_base"], name='feed')
	Xtrans=pp.transition(cross_section1=X1, cross_section2=X2, width_type='linear')
	
	X1_cutout=CrossSection()
	X1_cutout.add(width=80, offset=0, layer=layers["gnd"], name='cutout')
	X2_cutout=CrossSection()
	X2_cutout.add(width=1067, offset=0, layer=layers["gnd"], name='cutout')
	Xtrans_cutout=pp.transition(cross_section1=X1_cutout, cross_section2=X2_cutout, width_type='linear')

	#top end of feedline (turn around)
	start=top_port
	P_top=Path()
	s0 = pp.straight(length=1000)
	s1=pp.euler(radius=500, angle=90)
	s2 = pp.straight(length=10000)
	s3 = pp.euler(radius=500, angle=-90)
	s4 = pp.straight(length=1300)
	P_top.append([s0, s1, s2, s3, s4])
	trans_top=P_top.extrude(Xtrans)
	P_top.append([pp.straight(length=800)])
	cutout_top = P_top.extrude(Xtrans_cutout)
	C.add_ref(trans_top).rotate(150).move(start)
	N.add_ref(cutout_top).rotate(150).move(start)

	#bottom of feedline
	start=F[0][0]
	P_bottom = Path()
	s0 = pp.straight(length=1000)
	s1 = pp.euler(radius=500, angle=-90)
	s2 = pp.straight(length=10000)
	s3 = pp.euler(radius=500, angle=90)
	s4 = pp.straight(length=1500)
	P_bottom.append([s0, s1, s2, s3, s4])
	trans_bottom = P_bottom.extrude(Xtrans)
	P_bottom.append([pp.straight(length=800)])
	cutout_bottom = P_bottom.extrude(Xtrans_cutout)
	C.add_ref(trans_bottom).rotate(150).move(start)
	N.add_ref(cutout_bottom).rotate(150).move(start)




	return C, N


##############################################################3
# FOR MAKING A 25mm SQUARE CHIP
########################################################

#right now, the cap sizes just change by 10um
def place_pixels_chip(design, cap_sizes):

	count=0
	D = Device()

	#GND=Device()
	NO_GND=Device()

	row_polarity=1

	feedline_array=[]
	points=[]
	
	offset = tile_sidelength/2.

	x=tile_sidelength/2.
	if row_polarity<0: 
			x+=offset
	y=tile_sidelength/2.

	fx = 0
	fy = tile_sidelength
	#if row_polarity<0: 
	#		fy+=np.sin(60*np.pi/180.)*tile_sidelength


	#left to right, top to bottom
	for line in list(reversed(design)):

		fx=x-tile_sidelength/2.

		for i in range(len(line)):

			char=line[i]

			#place the tile
			t=tile(char, cap_sizes[count*2], cap_sizes[count*2+1])
			if char in ['H', 'Z', 'N', 'I']: count+=1
			D.add_ref(t).move([x,y])

			#add feedline points
			#over
			if char in ['H', 'Z', 'N', 'I', 'G']:
				points.append((fx, fy-tile_sidelength/2. + factor*tile_sidelength/3.))
				points.append((fx+tile_sidelength/2., fy-tile_sidelength/2 + factor*2*tile_sidelength/3.))
				points.append((fx+tile_sidelength, fy-tile_sidelength/2. + factor*tile_sidelength/3.))

				#cpw bridges
				sio2_rect = geo.rectangle(size=(80,185), layer=layers['sio2']).movex(-40)
				D.add_ref(sio2_rect).movex(fx+tile_sidelength/2.).movey(fy-tile_sidelength/2 + factor*2*tile_sidelength/3.-120)
				bridge = Device()
				strap = geo.rectangle(size=(10,300), layer=layers['bridge']).movex(-5)
				pad = geo.rectangle(size=(112,80), layer=layers['bridge']).movex(-56)
				bridge.add_ref(strap).movey(-123.5)
				bridge.add_ref(pad).movey(-125)
				bridge.add_ref(pad).movey(100)
				D.add_ref(bridge).movex(fx+tile_sidelength/2.).movey(fy-tile_sidelength/2 + factor*2*tile_sidelength/3.-55)
				if line[i-1] != '-':
					D.add_ref(sio2_rect).movex(fx).movey(fy-tile_sidelength/2. + factor*tile_sidelength/3.-65)
					D.add_ref(bridge).movex(fx).movey(fy-tile_sidelength/2. + factor*tile_sidelength/3.)


				if char=='G':
					x+=tile_sidelength
					fx+=tile_sidelength 
					continue

				#gnd plane and cutout
				#NOTE: make this into an irregular hexagon (two triangles and a rectangle)
				triangle_fx_offset = pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall
				triangle_lo_fy_offset = -tile_sidelength/2. + factor*tile_sidelength/3.-circle_sep/2.
				#triangle_hi_fy_offset = -tile_sidelength/2 + factor*2*tile_sidelength/3.-circle_sep
				triangle_hi_fy_offset = triangle_lo_fy_offset + triangle_fx_offset*np.tan(np.pi/6.)
				bevel_1=[(fx+tile_sidelength/2.-120*np.cos(np.pi/6.), fy+triangle_hi_fy_offset-120*np.sin(np.pi/6.)), (fx+tile_sidelength/2.+120*np.cos(np.pi/6.), fy+triangle_hi_fy_offset-120*np.sin(np.pi/6.))]
				bevel_2 = [(bevel_1[0][0]+40, bevel_1[0][1]-40),(bevel_1[1][0]-40, bevel_1[1][1]-40)]
				triangle_points=[(fx+tile_sidelength/2. - triangle_fx_offset, fy+triangle_lo_fy_offset), bevel_1[0], bevel_2[0], bevel_2[1], bevel_1[1], (fx+tile_sidelength/2.+triangle_fx_offset, fy+triangle_lo_fy_offset)]
				#no_gnd=geo.circle(radius=pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall, layer=layers["gnd"]).movex(x).movey(y)
				rect_cutout_width = 2*(pix_radius-feed_width-2*cpw_gap-cpw_gnd_wall)
				rect_cutout_height = tile_sidelength + 2*triangle_lo_fy_offset
				no_gnd_rect = geo.rectangle(size=(rect_cutout_width, rect_cutout_height), layer=layers['gnd']).movex(x-rect_cutout_width/2.).movey(y-rect_cutout_height/2.)
				NO_GND.add_ref(no_gnd_rect)
				triangle=Device()
				triangle.add_polygon(triangle_points, layer=layers['gnd'])
				NO_GND.add_ref(triangle)
				NO_GND.add_ref(triangle).mirror(p1=[fx, fy-tile_sidelength/2.], p2=[fx+tile_sidelength, fy-tile_sidelength/2.])
				#gnd_blank = geo.rectangle(size=(tile_sidelength*1.2, tile_sidelength*1.2), layer=layers["gnd"]).movex(fx).movey(fy-tile_sidelength)
				#GND.add_ref(gnd_blank)

				
			x+=tile_sidelength
			fx+=tile_sidelength

		#increment tile info
		x=tile_sidelength/2.
		if row_polarity>0: 
			x+=offset
		y+=factor*tile_sidelength

		#make feedline
		print(count)
		path=comp.polypath_from_points(xypoints = points, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="circular bend", bend_radius=100)
		inv_cpw=comp.polypath_from_points(xypoints = points, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="circular bend", bend_radius=100)
		D.add_ref(path)
		NO_GND.add_ref(inv_cpw)
		feedline_array.append(points)
		points=[]
		fy+=factor*tile_sidelength

		row_polarity*= -1

	#D.add_ref(NO_GND)
	#gnd_plane = geo.boolean(A=[GND], B=[NO_GND], operation='A-B', layer=layers['gnd'])	
	#D.add_ref(gnd_plane)

	print('Total pixel count: ' + str(count))

	return D, feedline_array, NO_GND


def connect_feedlines_chip(F):
	C = Device(name='C')
	N=Device()

	i=0
	pointer = 0
	while i < len(F)-1:


		if pointer == 0:
		#right side
			start=F[i][-1]
			end=F[i+1][-1]
			prev=F[i][-2]
			connect=[(prev[0]+ (start[0]-prev[0])/2., prev[1] + (start[1]-prev[1])/2.)]
			connect.append(start)
			connect.append((start[0]+tile_sidelength/2., start[1]+ factor*tile_sidelength/3.))
			connect.append(end)
			nex=F[i+1][-2]
			connect.append((end[0]+ (nex[0]-end[0])/2., end[1] + (nex[1]-end[1])/2.))
			i+=1

		elif pointer == 1:
		#left side
			start=F[i][0]
			end=F[i+1][0]
			prev=F[i][1]
			connect=[(prev[0]+ (start[0]-prev[0])/2., prev[1] + (start[1]-prev[1])/2.)]
			connect.append(start)
			connect.append((start[0]-tile_sidelength/2., start[1]+ factor*tile_sidelength/3.))
			connect.append(end)
			nex=F[i+1][1]
			connect.append((end[0]+ (nex[0]-end[0])/2., end[1] + (nex[1]-end[1])/2.))
			i+=1

		else: pass

		pointer+=1
		pointer=pointer%2
		path = comp.polypath_from_points(xypoints=connect, lw = feed_width, name = None, inc_ports = True, layer = layers['nb_base'], corners="smooth")#"circular bend", bend_radius=100)
		C.add_ref(path)
		Npath = comp.polypath_from_points(xypoints=connect, lw = feed_width+2*cpw_gap, name = None, inc_ports = True, layer = layers['gnd'], corners="smooth")
		N.add_ref(Npath)


	C.add_port(name='p1', midpoint=F[-1][0], orientation=0)
	C.add_port(name='p2', midpoint=F[0][0], orientation=0)

	return C, N

