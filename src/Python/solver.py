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
pinMovement = 0.28
minPinPitch = 1.4
maxPerturbation = -1

# --------------------
#  Preparing Data
# --------------------

# Read input files
macros = []
nets = [] 
[macros, nets] = utils.readMacroNetFile(macroNetFile)
#constraint = utils.readConstraintFile(constraintFile)

# Group macros by type
[unique_macros, macro_types] = helpers.findUniqueMacros(macros)

# Process macro term location to macro-reference-location
unique_macros = helpers.processMacroTermLocation(unique_macros)

# Create macro point lists
[pointLists_x, pointLists_y] = helpers.createMacroPointList(unique_macros, pinMovement)
            # TODO: maybe problemtic due to createMPL
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

# Apply possible movement in each macro type
for macro in unique_macros:
	for term, macro_var, pointList_x, pointList_y in macro.terms, macro_vars, pointLists_x, pointLists_y:
		cplex_helpers.moveTermUpdate(mdl, term, pinMovement, macro_var, pointList_x, pointList_y)
		# TODO: maybe problemtic due to pointLists
# TODO: Rotation and Multi-copies

# Add Constraints
# minPinPitch Constraints
for macro in unique_macros:
	for i in [x for x in range(0, len(macro.terms))]:
		for j in [x for x in range(i, len(macro.terms))]:
			mdl.add(cplex_helpers.t2tDistance(mdl, macro.terms[i], macro.terms[j]) >= mdl.constant(minPinPitch))

# Add Objective
# Update terms info in all nets
helpers.updateTermsInNets(nets, macros)
# Express HPWL for each net/all nets
net_wl_list = []
for net in nets:
	net_wl = cplex_helpers.net_HPWL(mdl, net)
	net_wl_list.append(net_wl)

# TODO: get absolute Wmn expression
Wmn = mdl.sum(net_wl_list) / mdl.constant(len(net_wl_list))
mdl.add(minimize(Wmn))


# --------------------
#  Solve and display
# --------------------

# Solve Model
print("\nSolving model....")
msol = mdl.solve(TimeLimit=10)

# Print solution
if msol:
    print("Wmn: {}".format(msol.get_objective_values()[0]))
else:
    print("No solution found.")