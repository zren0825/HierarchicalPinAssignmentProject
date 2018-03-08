
import pdb
import sys
import os
import re
import operator

binary_variables=[]
timing_variables=[]

max_latency = 15
ASAP=False
ALAP=False

def exactILPScheduling(dataFlowGraph=None,costtable=None,ASAP=False,ALAP=False):
	ASAP=ASAP
	ALAP=ALAP
	solverInput="./results/"+dataFlowGraph.name+"_CPLEX"+".lp"
	solverOutput="./results/"+dataFlowGraph.name+"_CPLEX"+".results"
	generateILPModel(dataFlowGraph,costtable,filename=solverInput)
	comm="time python ./qcpex.py {f} o > {f2}".format(f=solverInput,f2=solverOutput)
	os.system(comm)

	result_hash = interpretCPLEX(filename=solverOutput)

	scheduling_results = {}
	for i in range(max_latency):
		scheduling_results[i]=[]

	for node in dataFlowGraph.nodes:
		for i in range(node.asap, node.alap):
			name=generateNodeControlStep(node,i)
			if result_hash[name]==1:
				node.start_time = i
				break
		for resource in costtable.nodeRes_table[node]:
			name=mappingName(node,resource)
			if result_hash[name]==1:
				node.assigned_resource=resource
				break
		for l in range(node.assigned_resource.latency):
			scheduling_results[node.start_time+l].append((node.name, node.assigned_resource.name))

	for i in range(1, max_latency):
		print i , scheduling_results[i]


def interpretCPLEX(filename):
	solver_hash = {}
	start_record = False
	f = open(filename,'r')
	for line in f.readlines():
		if not re.search("\w+",line):
			continue

		if re.search("Maximum bound violation",line):
			start_record = False

		if start_record:
			binding_line = re.split(':',line)
			for item in re.split(" *",binding_line[0]):	## cutting out spaces at both ends
				if re.search("\w",item):
					variable = item
			value = re.split('=', binding_line[1])[-1]
			value = re.split(" *",value)[1]
			value = re.split("\n",value)[0]
			if not variable in solver_hash.keys():
				solver_hash[variable]=float(value)

		if re.search("Objective value",line) != None:
			value = re.split(' *= *',line)[1]
			value = re.split("\n",value)[0]
			solver_hash['Objective value']=float(value)
			start_record = True

	if solver_hash == {}:
		pdb.set_trace()
		print("no solution for rule {rid} during bottom-up scheduling".format(rid = self.associated_rule.id))
		pdb.set_trace()

	f.close()

	return solver_hash

def generateILPModel(dfg,cost_table,filename=''):
	global binary_variables, timing_variables

	ilpstr=''
	ilpstr=ilpstr+generateObjectives(dfg,cost_table)
	ilpstr=ilpstr+generateNodeConstraints(dfg,cost_table)
	if not (ASAP or ALAP):
		ilpstr=ilpstr+generateResourceConcurrencyConstraints(dfg,cost_table)

	binary_variables=list(set(binary_variables))
	timing_variables=list(set(timing_variables))
	ilpstr=ilpstr+generateVarBounds()
	ilpstr=ilpstr+generateVarTypes()
	ilpstr=ilpstr+"End\n"

	f=None
	if filename=='':
		f=sys.stdout
	else:
		f=open(filename,'w')
	f.write(ilpstr)
	if filename!='':
		f.close()

def generateObjectives(dfg,cost_table):
	bstr='\nMinimize\n'
	bstr=bstr+"\t obj : latency\n"
	bstr=bstr+"\nSubject To\n"
	for sink in dfg.sinks:
		bstr=bstr+"latency - "+generateNodeStartTime(sink) + " - " + generateNodeLatency(sink) + " >= 0\n"
	return bstr

def generateNodeConstraints(dfg,cost_table):
	bstr = ""
	topological_sort = dfg.topologicalSort(source2sink=True)
	sorted_levels = sortDictByKeys(topological_sort)
	bstr = bstr  + generateNodeControlStepConstraints(sorted_levels)
	bstr = bstr + generateNodeDependencyConstraints(sorted_levels)
	bstr = bstr + generateNodeMappingConstraints(sorted_levels,cost_table)
	return bstr

def generateNodeControlStepConstraints(sorted_levels):
	bstr="\n\\ Node Control Step Constraints\n"
	for (level, nodes) in sorted_levels:
		for node in nodes:
			bstr = bstr + generateNodeStartTime(node)
			for i in range(node.asap, node.alap):
				bstr = bstr + " - {i} ".format(i=i) + generateNodeControlStep(node,i)
			bstr = bstr + " = 0\n" 
			stepnames=[]
			for i in range(node.asap,node.alap):
				stepnames.append(generateNodeControlStep(node,i))
			bstr=bstr + " + ".join(stepnames) + ' = 1\n'
	return bstr

def generateNodeDependencyConstraints(sorted_levels):
	bstr="\n\\ Dependency Concurrency\n"
	for (level, nodes) in sorted_levels:
		for node in nodes:
			for edge in node.going_out_edges:
				bstr = bstr + generateNodeStartTime(node) + " + "+generateNodeLatency(node) + " - " + generateNodeStartTime(edge.tail) + " <= 0\n" 
	return bstr

def generateNodeMappingConstraints(sorted_levels,cost_table):
	bstr = "\n\\ Mapping Constraints\n"
	for (level,nodes) in sorted_levels:
		for node in nodes:
			resources = cost_table.nodeRes_table[node]
			bstr = bstr + generateMappingConstraints(node,resources)
			bstr = bstr + generateLatencyConstraints(node,resources)
	return bstr

def generateMappingConstraints(node,resources):
	bstr=''
	names=[]
	for res in resources:
		names.append(mappingName(node,res))
	bstr=bstr+"+".join(names)+"=1\n"
	return bstr

def generateLatencyConstraints(node,resources):
	bstr = ''
	bstr = bstr + generateNodeLatency(node)
	for res in resources:
		bstr = bstr + " - {rlatency} ".format(rlatency=res.latency) + mappingName(node,res)
	bstr = bstr + ' = 0\n'
	return bstr

def generateResourceConcurrencyConstraints(dfg,cost_table):
	bstr=""
	bstr=bstr+"\n\\ Resource Concurrency\n"
	for (res,nodes) in cost_table.res_nodes.items():
		bstr = bstr + generateResourceConcurrencyConstraint(res,nodes)
	return bstr

def generateResourceConcurrencyConstraint(res,nodes):
	bstr = '\n\\ \t Resource Concurrency Constraint for Resource {rid}\n'.format(rid=res.name)
	for step in range(res.latency+1,max_latency):
		step_vars = []
		for node in nodes:
			if node.asap > step:
				continue
			if node.alap < (step-res.latency):
				continue
			start_step = max(node.asap,step-res.latency)
			end_step= min(node.alap,step)
			for i in range(start_step,end_step):
				step_vars.append(generateNodeControlStep(node,i))
		bstr = bstr + " + ".join(step_vars) + " <= {num}\n".format(num=res.number)
	return bstr

def generateVarBounds():
	global binary_variables,timing_variables
	bstr="\n\\Bounds on Decisions Variables\n"
	bstr=bstr+"Bounds\n"
	for var in binary_variables:
		bstr=bstr+"0 <= %20s <= 1\n" % (var)

	for var in timing_variables:
		bstr=bstr+"0 <= %20s <= %d\n" % (var,100)
	return bstr

def generateVarTypes():
	global binary_variables
	bstr="General\n"
	for var in binary_variables:
		bstr=bstr+'\t'+var + '\n'
	return bstr

def generateNodeStartTime(node):
	global timing_variables
	newname =node.name+"_START"
	timing_variables.append(newname)
	return newname

def mappingName(node,res):
	global binary_variables
	newname =res.name+"_"+node.name
	binary_variables.append(newname)
	return newname

def generateNodeLatency(node):
	global timing_variables
	name=node.name+"_latency"
	timing_variables.append(name)
	return name

def generateNodeControlStep(node,step):
	global binary_variables
	name=node.name+ "_"+str(step)
	binary_variables.append(name)
	return name

def sortDictByKeys(dictionary):
	"""
	input: dictionary is a dictionary
	output: sorted_dict, a tuple sorted by keys of the dictionary
	"""
	sorted_dict = sorted(dictionary.iteritems(),key=operator.itemgetter(0))
	return sorted_dict
