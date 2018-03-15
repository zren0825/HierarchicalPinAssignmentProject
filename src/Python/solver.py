# This file contains implemention of CPLEX solver
# in the pin assignment task which are expected to be used
# as the main function in the CPLEX solver


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
file_path = '/w/class.2/ee/ee201a/ee201ota/submission/project/grade_16/'
designInfoFile = file_path + 'design_info.txt'

# --------------------
#  Preparing Data
# --------------------

# Read input files
macros = []
nets = [] 
macros, nets, pinMovement, minPinPitch, maxPerturbation = utils.readDesignInfoFile(designInfoFile)

pinMovement = int(float(pinMovement) * 2000)
minPinPitch = int(float(minPinPitch) * 2000)
if int(maxPerturbation) != -1:
	maxPerturbation = int(float(maxPerturbation) * 2000)
'''
# Update macro-reference location for all terms
for macro in macros:
		for term in macro.terms:
			term.update_term()
'''			
# Group macros by type
[unique_macros, macro_types] = helpers.findUniqueMacros(macros)

# Create macro point lists
for macro in macros:
	#helpers.createMacroPositionList(macro, pinMovement, minPinPitch)
	helpers.createMacroPositionList(macro, minPinPitch, minPinPitch)
'''
print(len(macros[0].positionList_x))
for i in range(0, len(macros[0].positionList_x)):
	print(str(macros[0].positionList_x[i]) + '\t' +  str(macros[0].positionList_y[i]))
'''
# --------------------
#  Build Model
# --------------------

# Create Model
mdl = CpoModel()

# Create Variables - move steps
new_index_map = dict()
for macro in unique_macros:
	for term in macro.terms:
		new_index = mdl.integer_var(0, len(macro.positionList_x), term.name)
		new_index_map[term.name] = new_index
'''
# Create Variable - macro.cpo_center.x/y : fix to macro.center.x/y in constraint
for macro in macros:
	macro.cpo_center.x = mdl.integer_var(domain = (macro.center.x, macro.center.x))
	macro.cpo_center.y = mdl.integer_var(domain = (macro.center.y, macro.center.y))
'''
# Apply possible movements in each term in each macro and update new cpo_location after movements 
for macro in macros:
	for term in macro.terms:
		cplex_helpers.moveTermUpdate(mdl, macro, term, new_index_map)
		
# TODO: Rotation 
# TODO: Multi-copies

# ----------------
# Add Constraints
# ----------------

# minPinPitch Constraints
'''
all_pins_list = []
for macro in macros:
	for term in macro.terms:
		all_pins_list.append(term)

for i in list(range(0, len(all_pins_list))):
	for j in list(range(i + 1, len(all_pins_list))):
		cpo_pinPitch = cplex_helpers.t2tDistance(mdl, all_pins_list[i], all_pins_list[j])
		mdl.add(cpo_pinPitch >= minPinPitch)
'''
new_index_list = []
for key, value in new_index_map.items():
	new_index_list.append(value)
for i in range(0, len(new_index_list)):
	for j in range(i+1, len(new_index_list)):
		mdl.add(new_index_list[i] != new_index_list[j])
		#mdl.add(new_index_list[i] - new_index_list[j] > minPinPitch/pinMovement)

		
# maxPinPitch Constraints - save cpo_perturbation_list for objectives modeling
cpo_perturbation_list = []
for macro in macros:
	for term in macro.terms:
		cpo_perturbation = cplex_helpers.termPerturbation(mdl, term)
		cpo_perturbation_list.append(cpo_perturbation)
		if maxPerturbation != -1:
			mdl.add(cpo_perturbation < maxPerturbation) 

# ----------------
# Add Objective
# ----------------
# Update terms info in all nets - because no initialization
helpers.updateTermsInNets(nets, macros)
# Collect original and new HPWL of each net
net_wl_list = []
original_net_wl_list = []
for net in nets:
	net_wl = cplex_helpers.net_HPWL(mdl, net)
	net_wl_list.append(net_wl)
	original_net_wl = helpers.net_HPWL(net)
	original_net_wl_list.append(original_net_wl)

# Max WL expression:  max net wirelength/max net wirelength without pin assignment
Wmax = mdl.max(net_wl_list)/int(max(original_net_wl_list))

# Mean WL expression: wirelength mean/wirelength mean without pin assignment
Wmn_new = mdl.sum(net_wl_list)/len(net_wl_list)
Wmn_ori = sum(original_net_wl_list)/len(original_net_wl_list)
Wmn = Wmn_new/int(Wmn_ori)
# perturbation expression: mean pin perturbation /(mean macro perimeter /2 )
perimeter_sum = 0
for macro in macros:
	perimeter_sum += macro.perimeter
perimeter_mean = perimeter_sum/len(macros)
pin_perturbation_mean = mdl.sum(cpo_perturbation_list)/len(cpo_perturbation_list)
Pmn = pin_perturbation_mean/int(perimeter_mean/2)

# Total Score
Wmax = mdl.max([0, 1 - Wmax])
Wmn = mdl.max([0, 1 - Wmn])
Pmn = mdl.max([0, 1 - Pmn])
m = 1 # subject to change After add pinCopy feature
e = 0 # Do not consider run-time score at runtime, set constraint manually
Score = 1*Wmax + 2*Wmn + 2*Pmn + 2*m 
mdl.add(mdl.maximize(Score))
#mdl.add(mdl.minimize(Pmn))

# --------------------
#  Solve and display
# --------------------

# Solve Model
print("\nSolving model....")
msol = mdl.solve(TimeLimit=1)

# Print solution
if msol:		
    # dump pin assignment decision to file to be read from c++ main
    utils.dumpOutputFile(msol, macros)
    # dump file to indicate python done
    utils.dumpFinishIndicatorFile()
    print("Python Script Done")
else:
    print("No solution found.")

 

