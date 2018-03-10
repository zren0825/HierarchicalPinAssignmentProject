# This file contains helper functions definitions
# in the pin assignment task which are expected to be used
# as helper functions in the CPLEX solver
# Last modified: 03/07/2018 3PM 

import basicDataStruc as ds

# ------------------------
#  Design Related Helpers
# ------------------------
def net_HPWL(net):
	x_max = net.terms[0].location.x
	x_min = net.terms[0].location.x
	y_max = net.terms[0].location.y
	y_min = net.terms[0].location.y
	for term in net.terms:
		x_max = term.location.x if (term.location.x > x_max) else x_max
		x_min = term.location.x if (term.location.x < x_min) else x_min
		y_max = term.location.y if (term.location.y > y_max) else y_max
		y_min = term.location.y if (term.location.y < y_min) else y_min
	return x_max - x_min + y_max - y_min

def find_Wmax(netList,original_netList):
	maxWL = max(netList, key = wireLength)
	original_maxWL = max(original_netList, key = wireLength)
	return max(0, 1 - maxWL/original_maxWL)

def find_Wmn(netList, original_netList):
	def calculateWL(nets):
		return sum(nets, key = wireLength)/len(nets)
	return max(0, 1 - calculateWL(netList)/calculateWL(original_netList))

def find_P(pins, macros):
	p_mean = sum(pins, key = perturbation)/len(pins)
	macro_perimeter_mean = sum(macros, key = perimeter)/len(macros)
	return max(0, 1 - p_mean/(macro_perimeter_mean/2))

def find_M(pins, original_pins):
	return 1 - (len(pins)-len(original_pins))/(len(original_pins))

def updateTermsInNets(nets, macros):
	for net in nets:
		for macro in macros:
			for term in macro.terms:
				if term.net.name == net.name:
					net.terms.append(term)

# --------------------------------
#  Solver Data Processing Helpers
# --------------------------------

def findUniqueMacros(macros):
	macro_types = set()
	unique_macros = []
	for macro in macros:
		if macro.type not in macro_types:
			macro_types.add(macro.type)
			unique_macros.append(macro)
	return unique_macros, macro_types

def processMacroTermLocation(unique_macros):
	for macro in unique_macros:
		for term in macro.terms:
			term.location.x -= term.macro.center.x 
			term.location.y -= term.macro.center.y
	return unique_macros

# TODO: OFFSET of pin size
def createMacroPointList(unique_macros, step):
	#count = 0
	pointLists_x = [] 
	pointLists_y = []
	for macro in unique_macros:
		for term in macro.terms:
			# WH
			half_width = int(abs(macro.box.upperLeft.x - macro.box.lowerRight.x)//2)
			half_height = int(abs(macro.box.upperLeft.y - macro.box.lowerRight.y)//2)
			
			pointList_x = []
			pointList_y = []
			# pin size offset
			size_offset = min( (abs(half_width - abs(term.macro_location.x)) , abs(half_height - abs(term.macro_location.y))))		
			# new_WH		
			new_half_width = half_width - size_offset
			new_half_height = half_height - size_offset
			# list start witt lowerLeft
			# Left
			for h in list(range(-new_half_height, new_half_height, step)):
				pointList_x.append(-new_half_width)
				pointList_y.append(h)
			# Top
			for w in list(range(-new_half_width, new_half_width, step)):
				pointList_x.append(w)
				pointList_y.append(new_half_height)
			# Right

			for h in list(range(new_half_height, -new_half_height, -step)):
				pointList_x.append(new_half_width)
				pointList_y.append(h)
			# Bottom
			for w in list(range(new_half_width, -new_half_width, -step)):
				pointList_x.append(w)
				pointList_y.append(-new_half_height)
			# match origin
			index = findCloestPoint(term, pointList_x, pointList_y)
			"""
			if(term.macro_location.x == new_half_width):
				term_edge = 'right'
			elif(term.macro_location.x == -new_half_width):
				term_edge = 'left'
			elif(term.macro_location.y == new_half_height):
				term_edge = 'top'
			else:
				term_edge = 'bottom'
			skew_offset = pointList_x[index] - term.macro_location.x if pointList_x[index] - term.macro_location.x != 0 else pointList_y[index] - term.macro_location.y
			"""
			# list start with default location
			pointList_x = pointList_x[index:len(pointList_x)] + pointList_x[0:index]
			pointList_y = pointList_y[index:len(pointList_y)] + pointList_y[0:index]			
			term.pointList_x = pointList_x
			term.pointList_y = pointList_y
			#count = 1
	


def findCloestPoint(term, pointList_x, pointList_y):
	index = 1
	min_index = 0
	min_dist = abs(term.macro_location.x - pointList_x[0]) + abs(term.macro_location.y - pointList_y[0])
	for point_x, point_y in zip(pointList_x, pointList_y):
		distance = abs(term.macro_location.x - point_x) + abs(term.macro_location.y - point_y)
		if distance < min_dist:
			min_dist = distance 
			min_index = index
		index = index + 1
	return min_index


def moveTerm(term, moveDistance): # default move clockwise
	def updateTop(term, width, height, moveDistance):
		term.macro_location.x = width/2 + moveDistance
		term.macro_location.y = height/2
		term.edge = 'top'
	def updateRight(term, width, height, moveDistance):
		term.macro_location.x = width/2
		term.macro_location.y = height/2 - moveDistance 
		term.edge = 'right'
	def updateBottom(term, width, height, moveDistance):
		term.macro_location.x = width/2 - moveDistance
		term.macro_location.y = -height/2
		term.edge = 'bottom'
	def updateLeft(term, width, height, moveDistance):
		term.macro_location.x = -width/2
		term.macro_location.y = -height/2 + moveDistance
		term.edge = 'left'

	width = abs(term.macro.box.upperLeft.x - term.macro.box.lowerRight.x)
	height = abs(term.macro.box.upperLeft.y - term.macro.box.lowerRight.y)
	if term.edge == '':
		print("Error: Edge not defined!")
	
	if term.edge == 'top':
		distance = width/2 - term.macro_location.x if term.macro_location.x >= 0 else  width/2 + abs(term.macro_location.x)
		# On the same edge
		if moveDistance < distance:
			term.macro_location.x +=  moveDistance
		else:
			# On next edge
			moveDistance -= distance
			if moveDistance < height:
				updateRight(term, width, height, moveDistance)
			else:
				# On opposite edge
				moveDistance -= height
				if moveDistance < width:
					updateBottom(term, width, height, moveDistance)
				else:
					# On last edge
					moveDistance -= width
					updateLeft(term, width, height, moveDistance)
	elif term.edge == 'bottom':
		distance = width/2 + term.macro_location.x if term.macro_location.x >= 0 else  width/2 - abs(term.macro_location.x)
		# On the same edge
		if moveDistance < distance:
			term.macro_location.x -=  moveDistance
		else:
			# On next edge
			moveDistance -= distance
			if moveDistance < height:
				updateLeft(term, width, height, moveDistance)
			else:
				# On opposite edge
				moveDistance -= height
				if moveDistance < width:
					updateTop(term, width, height, moveDistance)
				else:
					# On last edge
					moveDistance -= width
					updateRight(term, width, height, moveDistance)
	elif term.edge == 'right':
		distance = term.macro_location.y + height/2 if term.macro_location.y >= 0 else  height/2 - abs(term.macro_location.y)
		# On the same edge
		if moveDistance < distance:
			term.macro_location.y -=  moveDistance
		else:
			# On next edge
			moveDistance -= distance
			if moveDistance < width:
				updateBottom(term, width, height, moveDistance)
			else:
				# On opposite edge
				moveDistance -= height
				if moveDistance < height:
					updateLeft(term, width, height, moveDistance)
				else:
					# On last edge
					moveDistance -= height
					updateTop(term, width, height, moveDistance)
	else:
		distance = height/2 - term.macro_location.y if term.macro_location.y >= 0 else height/2 + abs(term.macro_location.y)
		# On the same edge
		if moveDistance < distance:
			term.macro_location.y +=  moveDistance
		else:
			# On next edge
			moveDistance -= distance
			if moveDistance < width:
				updateTop(term, width, height, moveDistance)
			else:
				# On opposite edge
				moveDistance -= height
				if moveDistance < height:
					updateRight(term, width, height, moveDistance)
				else:
					# On last edge
					moveDistance -= height
					updateBottom(term, width, height, moveDistance)
		
	term.update_location()
