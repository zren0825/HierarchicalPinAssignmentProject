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
"""
print(macros[0].name)
print(macros[0].type)
print(macros[0].perimeter)
print(macros[0].center.x)
print(macros[0].center.y)
print('----')
print(macros[0].terms[0].name)
print(macros[0].terms[0].type)
print(macros[0].terms[0].macro.name)
print(macros[0].terms[0].macro.center.x)
print(macros[0].terms[0].macro.center.y)
print(macros[0].terms[0].location.x)
print(macros[0].terms[0].location.y)
print(macros[0].terms[0].macro_location.x)
print(macros[0].terms[0].macro_location.y)
print(macros[0].terms[0].net.name)
print(macros[0].terms[0].edge)
print('----')
print(nets[0].terms[0].name)
print(nets[0].terms[0].type)
print(nets[0].terms[0].location.x)
print(nets[0].terms[0].location.y)
print(nets[0].terms[0].macro_location.x)
print(nets[0].terms[0].macro_location.y)
print(nets[0].terms[0].net.name)
print(nets[0].terms[0].edge)
"""


# Group macros by type
[unique_macros, macro_types] = helpers.findUniqueMacros(macros)
"""
print(len(unique_macros))
print(unique_macros[0].name)
print(unique_macros[0].perimeter)
print(unique_macros[0].center.x)
print(unique_macros[0].center.y)
print(unique_macros[0].terms[0].name)
print(unique_macros[0].terms[0].type)
print(unique_macros[0].terms[0].macro.name)
print(unique_macros[0].terms[0].macro_location.x)
print(unique_macros[0].terms[0].macro_location.y)
"""
# Process macro term location to macro-reference-location
unique_macros = helpers.processMacroTermLocation(unique_macros)
"""
print(unique_macros[0].terms[0].location.x)
print(unique_macros[0].terms[0].location.y)
print(unique_macros[0].terms[0].macro_location.x)
print(unique_macros[0].terms[0].macro_location.y)
"""


# Create macro point lists
helpers.createMacroPointList(unique_macros, pinMovement)
"""
print('-----------------')
print(unique_macros[0].perimeter//pinMovement)
print(len(unique_macros[0].terms[0].pointList_x))

print(unique_macros[0].terms[0].pointList_x[0])
print(unique_macros[0].terms[0].macro_location.x)
"""

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

# Create Variable - step : fix to pinMovement in constraint
pinMovement_var = mdl.integer_var(0, pinMovement)

# Create Variable - macro.cpo_center.x/y : fix to macro.center.x/y in constraint
for macro in macros:
	macro.cpo_center.x = mdl.integer_var(0, macro.center.x)
	macro.cpo_center.y = mdl.integer_var(0, macro.center.y)
# Apply possible movement in each macro type


for i in range(0, len(unique_macros)):
	for j in range(0, len(unique_macros[i].terms)):
		#print(unique_macros[i].terms[j].name)
		#print(type((macro_vars[i])[j]))
		#print('--------------------------')
		cplex_helpers.moveTermUpdate(mdl, unique_macros[i].terms[j], pinMovement_var, (macro_vars[i])[j])

print(type(unique_macros[0].terms[0].cpo_location.x))
print('--------------------------')
		# TODO: maybe problemtic due to pointLists
# TODO: Rotation and Multi-copies

# ----------------
# Add Constraints
# ----------------

# fixed variable constraints
mdl.add(pinMovement_var == pinMovement) 
for macro in macros:
	mdl.add(macro.cpo_center.x == macro.center.x)
	mdl.add(macro.cpo_center.y == macro.center.y)
# minPinPitch Constraints
"""
for macro in unique_macros:
	for i in [x for x in range(0, len(macro.terms))]:
		for j in [x for x in range(i, len(macro.terms))]:
			a = True
			#mdl.add(cplex_helpers.t2tDistance(mdl, macro.terms[i], macro.terms[j]) >= mdl.constant(minPinPitch))
"""
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
    #print("Wmn: {}".format(msol.get_objective_values()[0]))
    print("Done")
else:
    print("No solution found.")