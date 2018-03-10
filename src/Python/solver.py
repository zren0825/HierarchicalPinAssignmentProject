# This file contains implemention of CPLEX solver
# in the pin assignment task which are expected to be used
# as the main function in the CPLEX solver
# Last modified: 03/07/2018 3PM 

from docplex.cp.model import CpoModel
import basicDataStruc as ds
import utils
import helpers
import cplex_helpers
# --------------------
#  Define Parameters
# --------------------
"""
pinLayer	6
minRoutingLayer	7
maxRoutingLayer	9
pinMovement	0.28
minPinPitch	1.4
maxPerturbation	-1
"""
macroNetFile = 'cplex_for_python.txt'
#constraintFile = ''
pinMovement = int(0.28 * 2000)
minPinPitch = int(1.4 * 2000)
maxPerturbation = -1

# --------------------
#  Preparing Data
# --------------------

# Read input files
macros = []
nets = [] 
[macros, nets] = utils.readMacroNetFile(macroNetFile)
#constraint = utils.readConstraintFile(constraintFile)
# Update all terms
for macro in macros:
		for term in macro.terms:
			term.update_term()

# Group macros by type
[unique_macros, macro_types] = helpers.findUniqueMacros(macros)

# Process macro term location to macro-reference-location
unique_macros = helpers.processMacroTermLocation(unique_macros)

# Create macro point lists
helpers.createMacroPointList(unique_macros, pinMovement)

#print(unique_macros[0].terms[0].pointList_x)
# TODO: maybe problemtic due to createMPL
"""
print(helpers.t2tDistance(unique_macros[0].terms[0], unique_macros[0].terms[1]))
helpers.moveTermUpdate(unique_macros[0].terms[0], 60)
helpers.moveTermUpdate(unique_macros[0].terms[1], 0)
print(helpers.t2tDistance(unique_macros[0].terms[0], unique_macros[0].terms[1]))
"""
# --------------------
#  Build Model
# --------------------

# Create Model
mdl = CpoModel()
# Create Variables - moveDistance
macro_vars = []
for macro in unique_macros:
	macro_var = mdl.integer_var_list(len(macro.terms), 0, int(macro.perimeter/pinMovement), macro.type)
	macro_vars.append(macro_var)

# Create Variable - macro.cpo_center.x/y : fix to macro.center.x/y in constraint
for macro in macros:
	macro.cpo_center.x = mdl.integer_var(0, macro.center.x)
	macro.cpo_center.y = mdl.integer_var(0, macro.center.y)

# Apply possible movement in each macro type
for i in range(0, len(unique_macros)):
	for j in range(0, len(unique_macros[i].terms)):
		cplex_helpers.moveTermUpdate(mdl, unique_macros[i].terms[j], (macro_vars[i])[j])

# TODO: maybe problemtic due to pointLists
# TODO: Rotation and Multi-copies

# ----------------
# Add Constraints
# ----------------

# fixed variable constraints
for macro in macros:
	mdl.add(macro.cpo_center.x == macro.center.x)
	mdl.add(macro.cpo_center.y == macro.center.y)
# minPinPitch Constraints
mdl.add(cplex_helpers.t2tDistance(mdl, unique_macros[0].terms[0], unique_macros[0].terms[1]) >= minPinPitch)

for macro in unique_macros:
	for i in list(range(0, len(macro.terms))):
		for j in list(range(i + 1, len(macro.terms))):
			#print((i,j))
			mdl.add(cplex_helpers.t2tDistance(mdl, macro.terms[i], macro.terms[j]) >= minPinPitch)




# ----------------
# Add Objective
# ----------------
# Update terms info in all nets

helpers.updateTermsInNets(nets, macros)
# Express HPWL for each net/all nets
net_wl_list = []
for net in nets:
	net_wl = cplex_helpers.net_HPWL(mdl, net)
	net_wl_list.append(net_wl)

# TODO: get absolute Wmn expression
Wmn = mdl.sum(net_wl_list) #/ mdl.constant(len(net_wl_list))
mdl.add(mdl.minimize(Wmn))


# --------------------
#  Solve and display
# --------------------

# Solve Model
print("\nSolving model....")
msol = mdl.solve(TimeLimit=10)

# Print solution
if msol:
    parameters = msol.get_parameters()
    print(type(parameters))
    for i in range(0, len(unique_macros[0].terms)):
    	print(msol[(macro_vars[0])[i]])
    #print("Wmn: {}".format(msol.get_objective_values()[0]))
    print("Done")
else:
    print("No solution found.")