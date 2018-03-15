# This file contains utilization definitions
# in the pin assignment task which are expected to be used
# as utils functions in the CPLEX solver
# Last modified: 03/08/2018 

import basicDataStruc as ds
import helpers

def parseMacroBasicInfo(macro_basic_info_line):
	macro_info_chunks = macro_basic_info_line.split()
	macro = ds.Macro(name = macro_info_chunks[0])
	macro.type = macro_info_chunks[1][0:(len(macro_info_chunks[1])-len(macro_info_chunks[0]) - 1)]
	#macro.type = macro_info_chunks[1]
	UR = ds.Location(int(macro_info_chunks[2]), int(macro_info_chunks[3]))
	LL = ds.Location(int(macro_info_chunks[4]), int(macro_info_chunks[5]))
	macro.origin = ds.Location(int(macro_info_chunks[6]), int(macro_info_chunks[7]))
	macro.box = ds.Box(UR,LL)
	return macro

def parseNetBasicInfo(net_basic_info_line):
	net_info_chunks = net_basic_info_line.split()
	net = ds.Net(name = net_info_chunks[0])
	return net

def parseTerm(term_line, macro):
	term_info_chunks = term_line.split()
	term = ds.Term(term_info_chunks[1], term_info_chunks[2],term_info_chunks[3], ds.Location(int(term_info_chunks[4]), int(term_info_chunks[5])))
	term.macro = macro
	term.macro_location = ds.Location(term.location.x - term.macro.center.x,term.location.y - term.macro.center.y)
	
	return term

def readDesignInfoFile(input_file):
	macros = []
	nets = []
	f = open(input_file)
	pinMovement = f.readline().split()[1]
	minPinPitch = f.readline().split()[1]
	maxPerturbation = int(f.readline().split()[1])
	star = f.readline()
	line = f.readline()
	while line:
		if line == 'Macro\n':
			macro_basic_info = f.readline()
			macro = parseMacroBasicInfo(macro_basic_info)
			macro.update_macro()	
			line = f.readline()
			while line.split()[0] == 'T':
				term = parseTerm(line, macro)
				macro.terms.append(term)
				line = f.readline()
			macros.append(macro)
			 
		if line == 'Net\n':
			net_basic_info = f.readline()
			net = parseNetBasicInfo(net_basic_info)
			line = f.readline()
			while line.split()[0] == 'T':
				term = parseTerm(line, macro)
				net.terms.append(term)
				line = f.readline()
			nets.append(net)
		line = f.readline()
	f.close()
	return macros, nets, pinMovement, minPinPitch, maxPerturbation

def dumpOutputFile(msol, macros):
	decision = open("/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/pin_assignment_decision.txt","w")  
	for macro in macros:
		decision.write(macro.name + '\n')
		for term in macro.terms:
			term_name = str(msol.get_var_solution(term.name)).split(': ')[0]
			index = str(msol.get_var_solution(term.name)).split(': ')[1]
			x = macro.positionList_x[int(index)]
			y = macro.positionList_y[int(index)]

			decision.write(term_name + '\t' + index + '\t' + str(x) + '\t' + str(y) +'\n')
		decision.write(macro.name + '\n')
	decision.close() 

def dumpFinishIndicatorFile():
	done = open("/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/DecisionsMade.txt","w")  
	done.write("Decisions have been made.\n") 
	done.close()















