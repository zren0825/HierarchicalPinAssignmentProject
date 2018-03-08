# This file contains utilization definitions
# in the pin assignment task which are expected to be used
# as utils functions in the CPLEX solver
# Last modified: 03/08/2018 

import os
import basicDataStruc as ds

def parseMacroBasciInfo(macro_basic_info_line):
	macro_info_chunks = macro_basic_info_line.split()
	macro = ds.Macro(name = macro_info_chunks[0])
	macro.type = macro_info_chunks[1]
	macro.box = ds.Box(ds.Location(macro_info_chunks[2],macro_info_chunks[3]),ds.Location(macro_info_chunks[4],macro_info_chunks[5]))
	return macro

def parseNetBasciInfo(net_basic_info_line):
	net_info_chunks = net_basic_info_line.split()
	net = ds.Net(name = net_info_chunks[0])
	return net

def parseTerm(term_line):
	term_info_chunks = term_line.split()
	term = ds.Term(term_info_chunks[1], term_info_chunks[2], ds.Location(term_info_chunks[3], term_info_chunks[4]))
	return term

def readMacroNetFile(input_file):
	macros = []
	nets = []
	f = open(input_file)
	line = f.readline()
	#print(line.split(' '))
	while line:
		if line == 'Macro\n':
			macro_basic_info = f.readline()
			macro = parseMacroBasciInfo(macro_basic_info)
			line = f.readline()
			while line.split()[0] == 'T':
				term = parseTerm(line)
				macro.terms.append(term)
				line = f.readline()
			macro.update_perimeter()
			macros.append(macro)

		if line == 'Net\n':
			net_basic_info = f.readline()
			net = parseNetBasciInfo(net_basic_info)
			line = f.readline()
			while line.split()[0] == 'T':
				term = parseTerm(line)
				net.terms.append(term)
				line = f.readline()
			nets.append(net)

		line = f.readline()
	f.close()
	return macros, nets

#Testing readMacroNetFile()
#[macros, nets] = readMacroNetFile('simple_test_v0.txt')
#print(macros)
#print(nets)

def readConstraintFile(input_file):
	return 0
def dumpOutputFile(output_file):
	return 0