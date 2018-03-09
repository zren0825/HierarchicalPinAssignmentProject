# This file contains helper functions definitions
# in the pin assignment task which are expected to be used
# as helper functions in the CPLEX solver
# Last modified: 03/07/2018 3PM 

import basicDataStructure as ds

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

# --------------------------------
#  Solver Constraint Helpers
# --------------------------------

def t2t_distance(term1, term2):
	return abs(term1.macor_location.x - term2.macor_location.x) + abs(term1.macor_location.y - term2.macor_location.y)

# --------------------------------
#  Solver Optimizer Helpers
# --------------------------------





