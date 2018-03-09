# This file contains cplex helper functions definitions
# in the pin assignment task which are expected to be used
# as cplex helper functions in the CPLEX solver
# Last modified: 03/07/2018 3PM 

import docplex.cp.model as mdl
import helpers
def moveTermUpdate(term, step, moveDistance, pointList_x, pointList_y): # default move clockwise
	index = findCloestPoint(term, pointList_x, pointList_y)
	new_index = mdl.constant(index) + moveDistance/mdl.constant(step)
	# Update Cpo Location
	term.cpo_macro_location.x = mdl.element(pointList_x, new_index)
	term.cpo_macro_location.y = mdl.element(pointList_y, new_index)
	term.cpo_location.x = term.cpo_macro_location.x + mdl.constant(term.macron.center.x)
	term.cpo_location.y = term.cpo_macro_location.y + mdl.constant(term.macron.center.y)

def net_HPWL(net):
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