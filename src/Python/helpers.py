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
		center = ds.Location(abs(macro.box.upperLeft.x - macro.box.lowerRight.x)/2, 
							 abs(macro.box.upperLeft.y - macro.box.lowerRight.y)/2)
		for term in macro.terms:
			term.location.x -= center.x 
			term.location.y -= center.y
	return unique_macros

def createMacroPointList(unique_macros, step):
	pointLists_x = []
	pointLists_y = []
	for macro in unique_macros:
		pointList_x = []
		pointList_y = []
		width = int(abs(macro.box.upperLeft.x - macro.box.lowerRight.x)/2)
		height = int(abs(macro.box.upperLeft.y - macro.box.lowerRight.y)/2)

		# Left
		for h in [x * step for x in range(-height, height)]:
			pointList_x.append(-width)
			pointList_y.append(h)
		# Top
		for w in [x * step for x in range(-width, width)]:
			pointList_x.append(w)
			pointList_y.append(height)
		# Right

		for h in [x * -step for x in range(height, -height)]:
			pointList_x.append(width)
			pointList_y.append(h)
		# Bottom
		for w in [x * -step for x in range(width, -width)]:
			pointList_x.append(w)
			pointList_y.append(-height)
		pointLists_x.append(pointList_x)
		pointLists_y.append(pointList_y)

	return pointLists_x, pointLists_y
def findCloestPoint(term, pointList_x, pointList_y):
	index = 1
	res = ()
	min_index = 0
	min_dist = abs(term.macro_location.x - pointList_x[0]) + abs(term.macro_location.y - pointList_y[0])
	for point_x, point_y in pointList_x, pointList_y:
		distance = abs(term.macro_location.x - point_x) + abs(term.macro_location.y - point_y)
		if distance < min_dist:
			min_dist = distance 
			min_index = index
			res = point
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
