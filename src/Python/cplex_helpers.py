# This file contains cplex helper functions definitions
# in the pin assignment task which are expected to be used
# as cplex helper functions in the CPLEX solver


import helpers

# --------------------------------
#  Solver Constraint Helpers
# --------------------------------

def t2tDistance(mdl, term1, term2):
	return mdl.abs(term1.cpo_location.x - term2.cpo_location.x) + mdl.abs(term1.cpo_location.y - term2.cpo_location.y)

def termPerturbation(mdl, term):

	return mdl.abs(term.cpo_location.x - term.location.x) + mdl.abs(term.cpo_location.y - term.location.y) 

# --------------------------------
#  Solver Optimizer Helpers
# --------------------------------

def moveTermUpdate(mdl, macro, term, new_index_map): # default move clockwise

 	term.cpo_location.x = mdl.element(macro.positionList_x, new_index_map[term.name])
	term.cpo_location.y = mdl.element(macro.positionList_x, new_index_map[term.name])
	#term.cpo_location.x = macro.positionList_x[ new_index_map[term.name]]
	#term.cpo_location.y = macro.positionList_x[ new_index_map[term.name]]

def net_HPWL(mdl, net):
	terms_x = []
	terms_y = []
	for term in net.terms:
		terms_x.append(term.cpo_location.x)
		terms_y.append(term.cpo_location.y)
	x_max = mdl.max(terms_x)
	x_min = mdl.min(terms_x)
	y_max = mdl.max(terms_y)
	y_min = mdl.min(terms_y)

	return x_max - x_min + y_max - y_min
