import os
import math
import bezmisc
import re
import copy
import sys
import time
import cmath
import codecs
import random
import simplestyle
import inkex
import simplepath
import cubicsuperpath
import simpletransform


def atan2(*arg):
	if len(arg)==1 and( type(arg[0]) == type([0., 0.]) or type(arg[0]) == type((0.,0.)) ):
		return (math.pi/2 - math.atan2(arg[0][0], arg[0][1])) % math.pi2

	elif len(arg)==2:
		return (math.pi/2 - math.atan2(arg[0], arg[1])) % math.pi2
	else:
		raise ValueError, "Bad arguments for atan! (%s)" % arg

def point_to_point_d2(a,b):
	return (a[0]-b[0])**2 + (a[1]-b[1])**2


def gcode_comment_str(s, replace_new_line = False):
	if replace_new_line:
		s = re.sub(r"[\n\r]+", ".", s)
	res = ""
	if s[-1] == "\n" : s = s[:-1]
	for a in s.split("\n"):
		if a != "":
			res += "(" + re.sub(r"[\(\)\\\n\r]", ".", a) + ")\n"
		else:
			res += "\n"

	return res

def print_(*arg):
	f = open("C:/Personal File/inkscape_logfile.txt","a")
	for s in arg :
		s = str(unicode(s).encode('unicode_escape'))+" "
		f.write( s )
	f.write("\n")
	f.close()

class Postprocessor():
	def __init__(self, error_function_handler):	
		self.error = error_function_handler 
		self.functions = {
					"remap"		: self.remap,
					"remapi"	: self.remapi ,
					"scale"		: self.scale,
					"move"		: self.move,
					"flip"		: self.flip_axis,
					"flip_axis"	: self.flip_axis,
					"round"		: self.round_coordinates,
					"parameterize"	: self.parameterize,
					"regex"			: self.re_sub_on_gcode_lines
					}
	
			
	def process(self,command):
		command = re.sub(r"\\\\",":#:#:slash:#:#:",command)
		command = re.sub(r"\\;",":#:#:semicolon:#:#:",command)
		command = command.split(";")
		for s in command: 
			s = re.sub(":#:#:slash:#:#:","\\\\",s)
			s = re.sub(":#:#:semicolon:#:#:","\\;",s)
			s = s.strip()
			if s!="" :
				self.parse_command(s)		
			
	
	def parse_command(self,command):
		r = re.match(r"([A-Za-z0-9_]+)\s*\(\s*(.*)\)",command)
		if not r:
			self.error("Parse error while postprocessing.\n(Command: '%s')"%(command), "error")
		function, parameters = r.group(1).lower(),r.group(2)
		if function in self.functions :
			print_("Postprocessor: executing function %s(%s)"%(function,parameters))
			self.functions[function](parameters)
		else : 
			self.error("Unrecognized function '%s' while postprocessing.\n(Command: '%s')"%(function,command), "error")
	
	
	def re_sub_on_gcode_lines(self, parameters):
		gcode = self.gcode.split("\n")
		self.gcode = ""
		try :
			for line in gcode :
				self.gcode += eval( "re.sub(%s,line)"%parameters) +"\n"

		except Exception as ex :	
			self.error("Bad parameters for regexp. They should be as re.sub pattern and replacement parameters! For example: r\"G0(\d)\", r\"G\\1\" \n(Parameters: '%s')\n %s"%(parameters, ex), "error")				
		
	
	def remapi(self,parameters):
		self.remap(parameters, case_sensitive = True)
	
	
	def remap(self,parameters, case_sensitive = False):
		# remap parameters should be like "x->y,y->x"
		parameters = parameters.replace("\,",":#:#:coma:#:#:")
		parameters = parameters.split(",")
		pattern, remap = [], []
		for s in parameters:
			s = s.replace(":#:#:coma:#:#:","\,")
			r = re.match("""\s*(\'|\")(.*)\\1\s*->\s*(\'|\")(.*)\\3\s*""",s)
			if not r :
				self.error("Bad parameters for remap.\n(Parameters: '%s')"%(parameters), "error")
			pattern +=[r.group(2)]	
			remap +=[r.group(4)]	
		
		
		
		for i in range(len(pattern)) :
			if case_sensitive :
				self.gcode = ireplace(self.gcode, pattern[i], ":#:#:remap_pattern%s:#:#:"%i )
			else :
				self.gcode = self.gcode.replace(pattern[i], ":#:#:remap_pattern%s:#:#:"%i)
			
		for i in range(len(remap)) :
			self.gcode = self.gcode.replace(":#:#:remap_pattern%s:#:#:"%i, remap[i])
	
	
	def transform(self, move, scale):
		axis = ["xi","yj","zk","a"]
		flip = scale[0]*scale[1]*scale[2] < 0 
		gcode = ""
		warned = []
		r_scale = scale[0]
		plane = "g17"
		for s in self.gcode.split("\n"):
			# get plane selection: 
			s_wo_comments = re.sub(r"\([^\)]*\)","",s)
			r = re.search(r"(?i)(G17|G18|G19)", s_wo_comments)
			if r :
				plane = r.group(1).lower()
				if plane == "g17" : r_scale = scale[0] # plane XY -> scale x
				if plane == "g18" : r_scale = scale[0] # plane XZ -> scale x
				if plane == "g19" : r_scale = scale[1] # plane YZ -> scale y
			# Raise warning if scale factors are not the game for G02 and G03	
			if plane not in warned:
				r = re.search(r"(?i)(G02|G03)", s_wo_comments)
				if r :
					if plane == "g17" and scale[0]!=scale[1]: self.error("Post-processor: Scale factors for X and Y axis are not the same. G02 and G03 codes will be corrupted.","warning") 
					if plane == "g18" and scale[0]!=scale[2]: self.error("Post-processor: Scale factors for X and Z axis are not the same. G02 and G03 codes will be corrupted.","warning") 
					if plane == "g19" and scale[1]!=scale[2]: self.error("Post-processor: Scale factors for Y and Z axis are not the same. G02 and G03 codes will be corrupted.","warning") 
					warned += [plane]
			# Transform		
			for i in range(len(axis)) :
				if move[i] != 0 or scale[i] != 1:
					for a in axis[i] :
						r = re.search(r"(?i)("+a+r")\s*(-?)\s*(\d*\.?\d*)", s)
						if r and r.group(3)!="":
							s = re.sub(r"(?i)("+a+r")\s*(-?)\s*(\d*\.?\d*)", r"\1 %f"%(float(r.group(2)+r.group(3))*scale[i]+(move[i] if a not in ["i","j","k"] else 0) ), s)
			#scale radius R
			if r_scale != 1 :
				r = re.search(r"(?i)(r)\s*(-?\s*(\d*\.?\d*))", s)
				if r and r.group(3)!="":
					try:
						s = re.sub(r"(?i)(r)\s*(-?)\s*(\d*\.?\d*)", r"\1 %f"%( float(r.group(2)+r.group(3))*r_scale ), s)
					except:
						pass	

			gcode += s + "\n"
			
		self.gcode = gcode
		if flip : 
			self.remapi("'G02'->'G03', 'G03'->'G02'")


	def parameterize(self,parameters) :
		planes = []
		feeds = {}
		coords = []
		gcode = ""
		coords_def = {"x":"x","y":"y","z":"z","i":"x","j":"y","k":"z","a":"a"}
		for s in self.gcode.split("\n"):
			s_wo_comments = re.sub(r"\([^\)]*\)","",s)
			# get Planes
			r = re.search(r"(?i)(G17|G18|G19)", s_wo_comments)
			if r :
				plane = r.group(1).lower()
				if plane not in planes : 
					planes += [plane]
			# get Feeds
			r = re.search(r"(?i)(F)\s*(-?)\s*(\d*\.?\d*)", s_wo_comments)
			if r :
				feed  = float (r.group(2)+r.group(3))
				if feed not in feeds :
					feeds[feed] = "#"+str(len(feeds)+20)
					
			#Coordinates
			for c in "xyzijka" :
				r = re.search(r"(?i)("+c+r")\s*(-?)\s*(\d*\.?\d*)", s_wo_comments)
				if r :
					c = coords_def[r.group(1).lower()]
					if c not in coords :
						coords += [c]
		# Add offset parametrization
		offset = {"x":"#6","y":"#7","z":"#8","a":"#9"}
		for c in coords:
			gcode += "%s  = 0 (%s axis offset)\n" %  (offset[c],c.upper())
			
		# Add scale parametrization
		if planes == [] : planes = ["g17"]
		if len(planes)>1 :  # have G02 and G03 in several planes scale_x = scale_y = scale_z required
			gcode += "#10 = 1 (Scale factor)\n"
			scale = {"x":"#10","i":"#10","y":"#10","j":"#10","z":"#10","k":"#10","r":"#10"}
		else :
			gcode += "#10 = 1 (%s Scale factor)\n" % ({"g17":"XY","g18":"XZ","g19":"YZ"}[planes[0]])
			gcode += "#11 = 1 (%s Scale factor)\n" % ({"g17":"Z","g18":"Y","g19":"X"}[planes[0]])
			scale = {"x":"#10","i":"#10","y":"#10","j":"#10","z":"#10","k":"#10","r":"#10"}
			if "g17" in planes :
				scale["z"] = "#11"				
				scale["k"] = "#11"				
			if "g18" in planes :
				scale["y"] = "#11"				
				scale["j"] = "#11"				
			if "g19" in planes :
				scale["x"] = "#11"				
				scale["i"] = "#11"				
		# Add a scale 
		if "a" in coords:
			gcode += "#12  = 1 (A axis scale)\n" 
			scale["a"] = "#12"
		
		# Add feed parametrization 
		for f in feeds :
			gcode += "%s = %f (Feed definition)\n" % (feeds[f],f)

		# Parameterize Gcode		
		for s in self.gcode.split("\n"):
			#feed replace :
			r = re.search(r"(?i)(F)\s*(-?)\s*(\d*\.?\d*)", s)
			if r and len(r.group(3))>0:
				s = re.sub(r"(?i)(F)\s*(-?)\s*(\d*\.?\d*)", "F [%s]"%feeds[float(r.group(2)+r.group(3))], s)
			#Coords XYZA replace
			for c in "xyza" :
				r = re.search(r"(?i)(("+c+r")\s*(-?)\s*(\d*\.?\d*))", s)
				if r and len(r.group(4))>0:
					s = re.sub(r"(?i)("+c+r")\s*((-?)\s*(\d*\.?\d*))", r"\1[\2*%s+%s]"%(scale[c],offset[c]), s)

			#Coords IJKR replace
			for c in "ijkr" :
				r = re.search(r"(?i)(("+c+r")\s*(-?)\s*(\d*\.?\d*))", s)
				if r and len(r.group(4))>0:
					s = re.sub(r"(?i)("+c+r")\s*((-?)\s*(\d*\.?\d*))", r"\1[\2*%s]"%scale[c], s)

			gcode += s + "\n"
	
		self.gcode = gcode	

	
	def round_coordinates(self,parameters) :
		try: 
			round_ = int(parameters)
		except :	
			self.error("Bad parameters for round. Round should be an integer! \n(Parameters: '%s')"%(parameters), "error")		
		gcode = ""
		for s in self.gcode.split("\n"):
			for a in "xyzijkaf" :
				r = re.search(r"(?i)("+a+r")\s*(-?\s*(\d*\.?\d*))", s)
				if r : 
					
					if r.group(2)!="":
						s = re.sub(
									r"(?i)("+a+r")\s*(-?)\s*(\d*\.?\d*)", 
									(r"\1 %0."+str(round_)+"f" if round_>0 else r"\1 %d")%round(float(r.group(2)),round_),
									s)
			gcode += s + "\n"
		self.gcode = gcode
	

	def scale(self, parameters):
		parameters = parameters.split(",")
		scale = [1.,1.,1.,1.]
		try :
			for i in range(len(parameters)) :
				if float(parameters[i])==0 : 
					self.error("Bad parameters for scale. Scale should not be 0 at any axis! \n(Parameters: '%s')"%(parameters), "error")		
				scale[i] = float(parameters[i])
		except :
			self.error("Bad parameters for scale.\n(Parameters: '%s')"%(parameters), "error")
		self.transform([0,0,0,0],scale)		

	
	def move(self, parameters):
		parameters = parameters.split(",")
		move = [0.,0.,0.,0.]
		try :
			for i in range(len(parameters)) :
				move[i] = float(parameters[i])
		except :
			self.error("Bad parameters for move.\n(Parameters: '%s')"%(parameters), "error")
		self.transform(move,[1.,1.,1.,1.])		


	def flip_axis(self, parameters):
		parameters = parameters.lower()
		axis = {"x":1.,"y":1.,"z":1.,"a":1.}	
		for p in parameters: 
			if p in [","," ","	","\r","'",'"'] : continue
			if p not in ["x","y","z","a"] : 
				self.error("Bad parameters for flip_axis. Parameter should be string consists of 'xyza' \n(Parameters: '%s')"%(parameters), "error")
			axis[p] = -axis[p]
		self.scale("%f,%f,%f,%f"%(axis["x"],axis["y"],axis["z"],axis["a"]))	


class BatikPathToGCode(inkex.Effect):

	def export_gcode(self, gcode, no_hearders = False):
			
		if not no_headers:
			postprocessors.gcode = self.header + postprocessor.gocde + self.footer

		f = open("C:\/Personal File\/"+ "newoutput.ngc", "w")
		f.write(postprocessor.gcode)
		f.close()

	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--radio1", action="store", type="string", dest="radio1", default="string1", help="testing for plugin")
		self.OptionParser.add_option("--radio2", action="store", type="string", dest="radio2", default="string11", help="testing for radio button 2")
	

	def generate_gcode(self, curve, layer, depth):
		Zauto_scale = self.Zauto_scale[layer]
		tool = self.tools[layer][0]

		g = ""

		def c(c):
			c = [c[i] if i<len(c) else None for i in range(6)]

			if c[5] == 0: c[5]=None
			s,s1 = [" X", " Y", " Z", " I", " J", " K"], ["","","","",""]
			m,a = [1,1,1*Zauto_scale,1,1,1*Zauto_scale], [0,0,0,0,0,0]
			r = ''
			for i in range(6):
				if c[i] != None:
					r += s[i] + ("%f" % (c[i]*m[i]+a[i])) + s1[i]

			return r


		def calculate_angle(a, current_a):
			return min([abs(a-current_a%math.pi2+math.pi2), a+current_a-current_a%math.pi2_math.pi2], [abs(a-current_a%math.pi2-math.pi2), a+current_a-current_a%math.pi2-math.pi2], [abs(a-current_a%math.pi2), a+current_a-current_a%math.pi2])[1]

		if len(curve)==0 : return ""

		try:
			self.last_used_tool == None
		except:
			self.last_used_tool = None

		print_("Working on curve")
		print_(curve)

		if(tool != self.last_used_tool):
			# g += ( "(Change tool to %s)\n" % re.sub("\"'\(\)\\\\"," ", tool["name"]) ) + tool["tool change gcode"] + "\n"
			g += ( "(Change tool to %s)\n" % re.sub("\"'\(\)\\\\"," ", "Cylindrical cutter" ) ) + "(None)" + "\n"	

		# lg, zs, f = "G00", self.options.Zsafe, "F%f"%tool['feed']
		lg, zs, f = "G00", "10.000000", "F1000"
		current_a = 0
		g0_to_safe_distance = "G00" + c([None, None, zs]) + "\n"
		# penetration_feed = " F%s"%tool["penetration feed"]
		penetration_feed = " F1000"

		for i in range(1, len(curve)):
			s, si = curve[i-1], curve[i]
			feed = f if lg not in ['G01', 'G02', 'G03'] else ''
			if s[1] == 'move':
				# g += go_to_safe_distance + 'G00' + c(si[0]) + "\n" + tool['gcode before path'] +  "\n"
				g += go_to_safe_distance + 'G00' + c(si[0]) + "\n" + "\n"
				lg = 'G00'
			elif s[1] == 'end':
				g += go_to_safe_distance + '' + "\n"
				lg = 'G00'

			elif s[1] == 'line':
				if lg == "G00" : g += "G01" + c([None, None, s[5][0] + depth]) + penetration_feed + "(Penetrate)\n"
				g += "G01" + c(si[0] + s[5][1]+ depth) + feed + "\n"
				lg = "G01"

			elif s[1] == 'arc':
				r = [(s[2][0]-s[0][0]), (s[2][1]-s[0][1])]
				if lg == "G00" : g += "G01" + c([None,None,s[5][0] + depth]) + penetration_feed + "(Penetrate)\n"
				if (r[0]**2 + r[1]**2) > 0.05000**2:
					r1, r2 = (P(s[0])-P(s[2])), (P(si[0]) - P(s[2]))
					if(abs(r1.mag()-r2.mag()) < 0.001):
						g += ("G02" if s[3] < 0 else "G03") + c(si[0] + [s[5][1]+depth, (s[2][0]-s[0][0]), (s[2][1]-s[0][1]) ]) + feed + "\n"
					else:
						r = (r1.mag() + r2.mag()) / 2
						g += ("G02" if s[3] < 0 else "G03") + c(si[0] +s[5][1]+depth) + " R%f" % (r) + feed + "\n"

					lg = "G02"

				else:
					g += "G01" + c(si[0] + s[5][1]+depth) + feed + "\n"
					lg = "G01"

		if si[1] == "end":
			g += go_to_safe_distance + "\n"

		return g


	def transform(self, source_point, layer, reverse=False):
		if layer not in self.transform_matrix:
			for i in range(self.layers.index(layer), -1, -1):
				if self.layers[i] in self.orientation_points:
					break

			if self.layers[i] not in self.orientation_points:
				self.error(_("Orientation points for '%s' layer have not been found! Please add orientation points using Orientation tab!") % layer.get(inkex.addNS('label', 'inkscape')), "no_orientation_points")
			elif self.layers[i] in self.transform_matrix:
				self.transform_matrix[layer] = self.transform_matrix[self.layers[i]]
				self.Zcoordinates[layer] = self.Zcoordinates[self.layers[i]]
			else:
				orientation_layer = self.layers[i]
				if len(self.orientation_points[orientation_layer]) > 1:
					self.error(_("There are more than one orientation point group in '%s' layer") % orientation_layer.get(inkex.addNS('label', 'inkscape')), "more_than_one_orientation_point_groups")
				points = self.orientation_points[orientation_layer][0]
				if len(points)==2:
					points += [ [ [(points[1][0][1]-points[0][0][1])+points[0][0][0], -(points[1][0][0]-points[0][0][0]) + points[0][0][1]], [-(points[1][1][1]-points[0][1][1])+points[0][1][0], points[1][1][0]-points[0][1][0]+points[0][1][1]] ] ]

				if len(points)==3:
					print_("Layer '%s' Orientation points: " % orientation_layer.get(inkex.addNS('label', 'inkscape')))
					for point in points:
						print(point)

					self.Zcoordinates[layer] = [max(points[0][1][2], points[1][1][2]), min(points[0][1][2], points[1][1][2])]

					matrix = numpy.array([
								[points[0][0][0], points[0][0][1], 1, 0, 0, 0, 0, 0, 0]
								[0, 0, 0, points[0][0][0], points[0][0][1], 1, 0, 0, 0],
								[0, 0, 0, 0, 0, 0, points[0][0][0], points[0][0][1], 1],
								[points[1][0][0], points[1][0][1], 1, 0, 0, 0, 0, 0, 0],
								[0, 0, 0, points[1][0][0], points[1][0][1], 1, 0, 0, 0],
								[0, 0, 0, 0, 0, 0, points[1][0][0], points[1][0][1], 1],
								[points[2][0][0], points[2][0][1], 1, 0, 0, 0, 0, 0, 0],
								[0, 0, 0, points[2][0][0], points[2][0][1], 1, 0, 0, 0],
								[0, 0, 0, 0, 0, 0, points[2][0][0], points[2][0][1], 1]
							])

					if numpy.linalg.det(matrix) != 0:
						m = numpy.linalg.solve(matrix.numpy.array([[points[0][1][0]], [points[0][1][1]], [1], [points[1][1][0]], [points[1][1][1]], [1], [points[2][1][0]], [points[2][1][1]], [1]])).tolist()

						self.transform_matrix[layer] = [[m[j*3+i][0] for i in range(3)] for j in range(3)]

					else:
						self.error(_("Orientation points are wrong! (if there are two orientation points they should not be the same. If there are three orientation points they should not be in a straight line.)"),"wrong_orientation_points")
				else:
					self.error(_("Orientation points are wrong! (if there are two orientation points they should not be the same. If there are three orientation points they should not be in a straight line.)"),"wrong_orientation_points")


			self.transform_matrix_reverse[layer] = numpy.linalg.inv(self.transform_matrix[layer]).tolist()
			print_("\n Layer '%s' transformation matrixes:" % layer.get(inkex.addNS('label','inkscape')) )
			print_(self.transform_matrix)
			print_(self.transform_matrix_reverse)

			self.Zauto_scale[layer] = 1
			print_("Z automatic scale = %s (computed according orientation points)" % self.Zauto_scale[layer])

		x,y = source_point[0], source_point[1]
		if not reverse:
			t = self.transform_matrix[layer]
		else:
			t = self.transform_matrix_reverse[layer]

		return [t[0][0]*x+t[0][1]*y+t[0][2], t[1][0]*x+t[1][1]*y+t[1][2]]






	def transform_csp(self, csp_, layer, reverse = False):
		csp = [ [ [csp_[i][j][0][:], csp_[i][j][1][:], csp_[i][j][2][:]] for j in range(len(csp_[i]))] for i in range(len(csp_)) ]
		# for i in xrange(len(csp)):
		# 	for j in xrange(len(csp[i])):
		# 		for k in xrange(len(csp[i][j])):
		# 			csp[i][j][k] = self.transform(csp[i][j][k], layer, reverse)

		return csp

	def set_tool(self,layer):
#		print_(("index(layer)=",self.layers.index(layer),"set_tool():layer=",layer,"self.tools=",self.tools))
#		for l in self.layers:
#			print_(("l=",l))
		for i in range(self.layers.index(layer),-1,-1):
#			print_(("processing layer",i))
			if self.layers[i] in self.tools : 
				break
		if self.layers[i] in self.tools :
			if self.layers[i] != layer : self.tools[layer] = self.tools[self.layers[i]]
			if len(self.tools[layer])>1 : self.error(_("Layer '%s' contains more than one tool!") % self.layers[i].get(inkex.addNS('label','inkscape')), "more_than_one_tool")
			return self.tools[layer]
		else :
			self.error(_("Can not find tool for '%s' layer! Please add one with Tools library tab!") % layer.get(inkex.addNS('label','inkscape')), "no_tool_error")

	def get_transforms(self,g):
		root = self.document.getroot()
		trans = []
		while (g!=root):
			if 'transform' in g.keys():
				t = g.get('transform')
				t = simpletransform.parseTransform(t)
				trans = simpletransform.composeTransform(t,trans) if trans != [] else t
				print_(trans)
			g=g.getparent()
		return trans 


	def apply_transforms(self,g,csp, reverse=False):
		trans = self.get_transforms(g)
		if trans != []:
			if not reverse :
				simpletransform.applyTransformToPath(trans, csp)
			else :
				simpletransform.applyTransformToPath(self.reverse_transform(trans), csp)
		return csp

	def error(self, s, type_= "Warning"):
		notes = "Note "
		warnings = """
						Warning tools_warning
						orientation_warning
						bad_orientation_points_in_some_layers
						more_than_one_orientation_point_groups
						more_than_one_tool
						orientation_have_not_been_defined
						tool_have_not_been_defined
						selection_does_not_contain_paths
						selection_does_not_contain_paths_will_take_all
						selection_is_empty_will_comupe_drawing
						selection_contains_objects_that_are_not_paths
						Continue
						"""
		errors = """
						Error 	
						wrong_orientation_points	
						area_tools_diameter_error
						no_tool_error
						active_layer_already_has_tool
						active_layer_already_has_orientation_points
					"""
		s = str(s)
		if type_.lower() in re.split("[\s\n,\.]+", errors.lower()) :
			print_(s)
			inkex.errormsg(s+"\n")		
			sys.exit()
		elif type_.lower() in re.split("[\s\n,\.]+", warnings.lower()) :
			print_(s)
			inkex.errormsg(s+"\n")		
		elif type_.lower() in re.split("[\s\n,\.]+", notes.lower()) :
			print_(s)
		else :
			print_(s)
			inkex.errormsg(s)		
			sys.exit()


	def get_info(self):
		self.selected_paths = {}
		self.paths = {}		
		self.tools = {}
		self.orientation_points = {}
		self.graffiti_reference_points = {}
		self.layers = [self.document.getroot()]
		self.Zcoordinates = {}
		self.transform_matrix = {}
		self.transform_matrix_reverse = {}
		self.Zauto_scale = {}
		self.in_out_reference_points = []
		self.my3Dlayer = None

		def recursive_search(g, layer, selected=False):
			items = g.getchildren()
			items.reverse()
			for i in items:
				if selected:
					self.selected[i.get("id")] = i
				if i.tag == inkex.addNS("g",'svg') and i.get(inkex.addNS('groupmode','inkscape')) == 'layer':
					if i.get(inkex.addNS('label','inkscape')) == '3D' :
						self.my3Dlayer=i
					else :
						self.layers += [i]
						recursive_search(i,i)

				elif i.get('gcodetools') == "Gcodetools orientation group" :
					points = self.get_orientation_points(i)
					if points != None :
						self.orientation_points[layer] = self.orientation_points[layer]+[points[:]] if layer in self.orientation_points else [points[:]]
						print_("Found orientation points in '%s' layer: %s" % (layer.get(inkex.addNS('label','inkscape')), points))
					else :
						self.error(_("Warning! Found bad orientation points in '%s' layer. Resulting Gcode could be corrupt!") % layer.get(inkex.addNS('label','inkscape')), "bad_orientation_points_in_some_layers") 

				#Need to recognise old files ver 1.6.04 and earlier
				elif i.get("gcodetools") == "Gcodetools tool definition" or i.get("gcodetools") == "Gcodetools tool defenition"  :
					tool = self.get_tool(i)
					self.tools[layer] = self.tools[layer] + [tool.copy()] if layer in self.tools else [tool.copy()]
					print_("Found tool in '%s' layer: %s" % (layer.get(inkex.addNS('label','inkscape')), tool))

				elif i.get("gcodetools") == "Gcodetools graffiti reference point" :
					point = self.get_graffiti_reference_points(i)
					if point != [] :
						self.graffiti_reference_points[layer] = self.graffiti_reference_points[layer]+[point[:]] if layer in self.graffiti_reference_points else [point]
					else :
						self.error(_("Warning! Found bad graffiti reference point in '%s' layer. Resulting Gcode could be corrupt!") % layer.get(inkex.addNS('label','inkscape')), "bad_orientation_points_in_some_layers") 
				
				elif i.tag == inkex.addNS('path','svg'):
					if "gcodetools"  not in i.keys() :
						self.paths[layer] = self.paths[layer] + [i] if layer in self.paths else [i]  
						if i.get("id") in self.selected :
							self.selected_paths[layer] = self.selected_paths[layer] + [i] if layer in self.selected_paths else [i]  

				elif i.get("gcodetools") == "In-out reference point group" :
					items_ = i.getchildren()
					items_.reverse()
					for j in items_ :
						if j.get("gcodetools") == "In-out reference point" :
							self.in_out_reference_points.append( self.apply_transforms(j,cubicsuperpath.parsePath(j.get("d")))[0][0][1] )


				elif i.tag == inkex.addNS("g",'svg'):
					recursive_search(i,layer, (i.get("id") in self.selected) )

				elif i.get("id") in self.selected :
# xgettext:no-pango-format
					self.error(_("This extension works with Paths and Dynamic Offsets and groups of them only! All other objects will be ignored!\nSolution 1: press Path->Object to path or Shift+Ctrl+C.\nSolution 2: Path->Dynamic offset or Ctrl+J.\nSolution 3: export all contours to PostScript level 2 (File->Save As->.ps) and File->Import this file."),"selection_contains_objects_that_are_not_paths")
				
					
		recursive_search(self.document.getroot(),self.document.getroot())

		if len(self.layers) == 1 : 
			self.error(_("Document has no layers! Add at least one layer using layers panel (Ctrl+Shift+L)"),"Error")
		root = self.document.getroot() 

		if  root in self.selected_paths or root in self.paths :
			self.error(_("Warning! There are some paths in the root of the document, but not in any layer! Using bottom-most layer for them."), "tools_warning" )

		if  root in self.selected_paths :
			if self.layers[-1] in self.selected_paths :
				self.selected_paths[self.layers[-1]] += self.selected_paths[root][:]
			else :	
				self.selected_paths[self.layers[-1]] = self.selected_paths[root][:]
			del self.selected_paths[root]
			
		if root in self.paths :	
			if self.layers[-1] in self.paths :
				self.paths[self.layers[-1]] += self.paths[root][:]
			else :
				self.paths[self.layers[-1]] = self.paths[root][:]
			del self.paths[root]



	def get_orientation_points(self,g):
		items = g.getchildren()
		items.reverse()
		p2, p3 = [], []
		p = None
		for i in items:
			if i.tag == inkex.addNS("g",'svg') and i.get("gcodetools") == "Gcodetools orientation point (2 points)":
				p2 += [i]
			if i.tag == inkex.addNS("g",'svg') and i.get("gcodetools") == "Gcodetools orientation point (3 points)":
				p3 += [i]
		if len(p2)==2 : p=p2 
		elif len(p3)==3 : p=p3 
		if p==None : return None
		points = []
		for i in p :	
			point = [[],[]]	
			for  node in i :
				if node.get('gcodetools') == "Gcodetools orientation point arrow":
					point[0] = self.apply_transforms(node,cubicsuperpath.parsePath(node.get("d")))[0][0][1]
				if node.get('gcodetools') == "Gcodetools orientation point text":
					r = re.match(r'(?i)\s*\(\s*(-?\s*\d*(?:,|\.)*\d*)\s*;\s*(-?\s*\d*(?:,|\.)*\d*)\s*;\s*(-?\s*\d*(?:,|\.)*\d*)\s*\)\s*',get_text(node))
					point[1] = [float(r.group(1)),float(r.group(2)),float(r.group(3))]
			if point[0]!=[] and point[1]!=[]:	points += [point]
		if len(points)==len(p2)==2 or len(points)==len(p3)==3 : return points
		else : return None


	def effect(self):
		# layer = self.current_layer
		layer = self.document.getroot()
		group = inkex.etree.SubElement(layer, 'g')
		group.set("id", "layer2")
		group.set(inkex.addNS('label', 'inkscape'), "Layer 2")

		layer.append(group)


		from functools import partial
		def get_boundaries(points):
			minx,miny,maxx,maxy= None, None, None, None

			out = [[],[],[],[]]
			for p in points:
				if minx==p[0]:
					out[0]+=[p]

				if minx == None or p[0] < minx:
					minx = p[0]
					out[0] = [p]

				if miny==p[1]:
					out[1] += [p]

				if miny==None or p[1]<miny:
					miny=p[1]
					out[1]=[p]
				if maxx==p[0]:
					out[2]+=[p]

				if maxx==None or p[0] > maxx:
					maxx=p[0]
					out[2]=[p]

				if maxy== p[1]:
					out[3]+=[p]

				if maxy== None or p[1]>maxy:
					maxy=p[1]
					out[3]=[p]

			return out

		def remove_duplicates(points):
			i=0
			out=[]
			for p in points:
				for j in xrange(i,len(points)):
					if p==points[j]:points[j]=[None, None]

				if p!= [None, None]: out+=[p]

			i+=1
			return(out)

		def get_way_len(points):
			l=0
			for i in xrange(1,len(points)):
				l+=math.sqrt((points[i][0]-points[i-1][0])**2 + (points[i][1]-points[i-1][1])**2)
				return l


		def sort_dxfpoints(points):
			points=remove_duplocates(points)
			ways= [
				[3,0],
				[3,2],
				[1,0],
				[1,2],
				[0.3],
				[0,1],
				[2,3],
				[2,1],
			]

			minimal_way = []
			minimal_len = None
			minimal_way_type = None

			for w in ways:
				tpoints=points[:]
				cw=[]
				for j in xrange(0,len(points)):
					p=get_boundaries(get_bounderies(tpoints)[w[0]])[w[1]]
					tpoints.remove(p[0])
					cw+=p

				curlen = get_way_len(cw)

				if minimal_len==None or curlen < minimal_len:
					minimal_len=curlen
					minimal_way=cw
					minimal_way_type=w

			return minimal_way

		def sort_lines(lines):
			if len(lines)==0: return []
			lines = [ [key]+lines[key] for key in range(len(lines))]
			keys = [0]
			end_point = lines[0][3:]
			print_("!!!", lines, "\n", end_point)
			del lines[0]
			while len(lines)>0:
				dist = [[point_to_point_d2(end_point, lines[i][1:3]),i] for i in range(len(lines))]
				i = min(dist)[1]
				keys.append(lines[i][0])
				end_point = lines[i][3:]
				del lines[i]

			return keys

		def sort_curves(curves):
			lines = []
			for curve in curves:
				lines += [curve[0][0][0] + curve[-1][-1][0]]

			return sort_lines(lines)

		def print_dxfpoints(points):
			gcode = ""
			for point in points:
				# gcode += "(drilling dfxpoint)\nG00 Z%f\nG00 X%f Y%f\nG01 Z%f F%f\nG04 P%f\nG00 Z%f\n" % (self.options.Zsafe,point[0],point[1],self.Zcoordinates[layer][1],self.tools[layer][0]["penetration_feed"], 0.2, self.options.Zsafe)
				gcode += "(drilling dfxpoint)\nG00 Z10.00000\nG00 X%f Y%f\nG01 Z%f F1000\nG04 P0.2\nG00 Z10.00000\n" % (point[0], point[1], self.Zcoordinates[layer][1])

			return gcode

		def get_path_properties(node, recursive=True, tags={inkex.addNS('desc', 'svg'):"Description", inkex.addNS('title', 'svg') : "Title"}):
			res = {}
			done = False
			root = self.document.getroot()
			while not done and node != root:
				for i in node.getchildren():
					if i.tag in tags:
						res[tags[i.tag]] == i.text

					done = True

				node = node.getparent()

			return res

		# all_nodes = []
		# for id, node in self.selected.iteritems():
		# 	all_nodes.append(node)
			

		# inkex.errormsg(_(str(all_nodes)))
		# exit()
		self.get_info()

		# inkex.errormsg(_(str(len(self.current_layer))))
		# exit()

		if self.selected_paths == {}:
			paths = self.paths
			self.error(_("No paths are selected! Trying to work on all available paths."), "warning")

		else:
			paths = self.selected_paths
			print_(("self.layers=", self.layers))
			print_(("paths=", paths))

			colors = {}
			for layer in self.layers:
				if layer in paths:
					print_(("layer", layer))

					self.transform_csp([ [ [[0,0], [0,0], [0,0]], [[0,0],[0,0],[0,0]] ] ], layer)
					# self.set_tool(layer)
					curves = []
					dfxpoints = []

					try:
						depth_func = eval("lambda c,d,s: " + "d".strip('"'))
					except:
						self.error("Bad depth function! Enter correct function at Path to Gcode tab!")

					for path in paths[layer]:
						if "d" not in path.keys():
							self.error(_("Warning: One or more paths do not have 'd' parameter, try to Ungroup (Ctrl+Shift+G) and Object to Path (Ctrl+Shift+C)!"), "selection_contains_objects_that_are_not_paths")
							continue
						csp = cubicsuperpath.parsePath(path.get("d"))
						csp = self.apply_transforms(path, csp)
						id_ = path.get("id")
						def set_comment(match, path):
							if match.group(1) in path_keys():
								return path.get(match.group(1))
							else:
								return "None"

						comment = ""

						style = simplestyle.parseStyle(path.get("style"))
						colors[id_] = simplestyle.parseColor(style["stroke"] if "stroke" in style and style["stroke"] != "none" else "#000")
						if path.get("dxfpoint") == "1":
							tmp_curve = self.transform_csp(csp, layer)
							x=tmp_curve[0][0][0][0]
							y=tmp_curve[0][0][0][1]
							print_("got dfxpoint (scaled) at (%f,%f)" % (x,y))
							dfxpoints += [[x,y]]
						else:
							zd,zs = self.Zcoordinates[layer][1], self.Zcoordinates[layer][0]
							c = 1. - float(sum(colors[id_]))/255/3

							curves += [ [ [id_, depth_func(c,zd,zs), comment], [self.parse_curve([subpath], layer) for subpath in csp] ] ] 

					dfxpoints = sort_dxfpoints(dfxpoints)
					gcode+=print_dxfpoints(dfxpoints)

					for curve in curves:
						for subcurve in curve[1]:
							self.draw_curve(subcurve, layer)
					keys = range(len(curves))

					for key in keys:
						d = curves[key][0][1]
						for step in range(0, int(math.ceil(abs((zs-d)/"(None)")))):
							z = max(d, zs - abs("(None)" * (step+1)))

							gcode += gcode_comment_str("\nStart cutting path id: %s"%curves[key][0][0])
							if curves[key][0][2] != "()":
								gcode += curves[key][0][2]

							for curve in curves[key[1]]:
								gcode += self.generate_gcode(curve, layer, z)

							gcode += gcode_comment_str("End cutting path id: %s\n\n"%curves[key][0][0])

		self.export_gcode(gcode)




if __name__ == "__main__":
	e = BatikPathToGCode()
	e.affect()