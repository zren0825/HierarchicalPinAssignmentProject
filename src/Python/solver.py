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
	macro.cpo_center.x = mdl.integer_var(domain =  (macro.center.x))
	macro.cpo_center.y = mdl.integer_var(domain =  (macro.center.y))

# Apply possible movement in each macro type
for i in range(0, len(unique_macros)):
	for j in range(0, len(unique_macros[i].terms)):
		cplex_helpers.moveTermUpdate(mdl, unique_macros[i].terms[j], (macro_vars[i])[j])

# TODO: maybe problemtic due to pointLists
# TODO: Rotation and Multi-copies

# ----------------
# Add Constraints
# ----------------

# minPinPitch Constraints
for macro in unique_macros:
	for i in list(range(0, len(macro.terms))):
		for j in list(range(i + 1, len(macro.terms))):
			#print((i,j))
			cpo_pinPitch = cplex_helpers.t2tDistance(mdl, macro.terms[i], macro.terms[j])
			mdl.add(cpo_pinPitch >= minPinPitch)

# maxPinPitch Constraints
cpo_perturbation_list = []
for macro in unique_macros:
	for term in macro.terms:
		cpo_perturbation = cplex_helpers.termPerturbation(mdl, macro.terms[i], macro.terms[j])
		cpo_perturbation_list.append(cpo_perturbation)
		mdl.add(cpo_perturbation <= maxPerturbation) 



# ----------------
# Add Objective
# ----------------
# Update terms info in all nets
helpers.updateTermsInNets(nets, macros)
# Process/
net_wl_list = []
original_net_wl_list = []
for net in nets:
	net_wl = cplex_helpers.net_HPWL(mdl, net)
	net_wl_list.append(net_wl)
	original_net_wl = helpers.net_HPWL(net)
	original_net_wl_list.append(original_net_wl)

# TODO: get absolute Wmn expression  Wmn = max(0, 1 - .....)

# Max WL expression:  (max net wirelength) / (max net wirelength without pin assignment)
Wmax = mdl.max(net_wl_list)/mdl.integer_var(domain = (int(max(original_net_wl_list))))

# Mean WL expression: – (wirelength mean) / (wirelength mean without pin assignment)
Wmn_new = mdl.sum(net_wl_list)/mdl.integer_var(domain = (len(net_wl_list)))
Wmn_ori = sum(original_net_wl_list)/len(original_net_wl_list)
Wmn = Wmn_new/mdl.integer_var(domain = (int(Wmn_ori)))
# perturbation expression: (mean pin perturbation) / { (mean macro perimeter) / 2 }
perimeter_sum = 0
for macro in macros:
	perimeter_sum += macro.perimeter
perimeter_mean = perimeter_sum/len(macros)
Pmn = mdl.sum(cpo_perturbation_list)/mdl.integer_var(domain = (int(perimeter_mean/2)))

# Total Score
zero = mdl.integer_var(domain = (0))
one = mdl.integer_var(domain = (1))
two = mdl.integer_var(domain = (2))
Wmax = mdl.max(zero, one - Wmax)
Wmn = mdl.max(zero, one - Wmn)
Pmn = mdl.max(zero, one - Pmn)
m = one # subject to change After add pinCopy feature
e = zero # Do not consider run-time score at runtime, set constraint manually
Score = one*Wmax + two*Wmn + two*Pmn + two*m 
mdl.add(mdl.maximize(Score))


# --------------------
#  Solve and display
# --------------------

# Solve Model
print("\nSolving model....")
msol = mdl.solve(TimeLimit=10)

# Print solution
if msol:
	# utils.dumptOutputFile()
    parameters = msol.get_parameters()
    print(type(parameters))
    for i in range(0, len(unique_macros[0].terms)):
    	print(msol[(macro_vars[0])[i]])
    #print("Wmn: {}".format(msol.get_objective_values()[0]))
    print("Done")
else:
    print("No solution found.")