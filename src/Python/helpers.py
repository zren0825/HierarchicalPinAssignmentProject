# This file contains helper functions definitions
# in the pin assignment task which are expected to be used
# as helper functions in the CPLEX solver
# Last modified: 03/07/2018 3PM 

import basicDataStructure

#def calculate_wl(net):
# TODO: in C++ 

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

