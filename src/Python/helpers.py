# This file contains helper functions definitions
# in the pin assignment task which are expected to be used
# as helper functions in the CPLEX solver


import basicDataStruc as ds

# ------------------------
#  Design Related Helpers
# ------------------------

# --------------------------------
#  Solver Data Processing Helpers
# --------------------------------

def findUniqueMacros(macros):
	macro_types = set()
	unique_macros = []
	for macro in macros:
		if macro.type not in macro_types:
			macro_types.add(macro.type)
			unique_macros.append(macro)
	return unique_macros, macro_types



def updateTermsInNets(nets, macros): 
	for net in nets: 
		for macro in macros: 
			for term in macro.terms: 
				if term.net.name == net.name: 
					net.terms.append(term)

			
# Find all possible pin positions for a macro
def createMacroPositionList(macro, step, pin_pitch):
	# Macro Boundary
	bound_left = macro.box.lowerLeft.x
	bound_bottom = macro.box.lowerLeft.y
	bound_right = macro.box.upperRight.x
	bound_top = macro.box.upperRight.y
	# Width/Height
	width = abs(macro.box.upperRight.x - macro.box.lowerLeft.x)
	height = abs(macro.box.upperRight.y - macro.box.lowerLeft.y)
	# pin size offset
	pin_offset = min([abs(bound_left - macro.terms[0].location.x) , abs(bound_left - macro.terms[0].location.x), abs(bound_top - macro.terms[0].location.y), abs(bound_bottom - macro.terms[0].location.y)])
	bound_left = macro.box.lowerLeft.x + pin_offset
	bound_bottom = macro.box.lowerLeft.y + pin_offset
	bound_right = macro.box.upperRight.x - pin_offset
	bound_top = macro.box.upperRight.y -pin_offset
	# Get legal horizontal/vertical reference point
	h_done = False
	v_done = False
	for term in macro.terms: 
		# Distance from term to each edge  term to l/t/r/b
		t2l = abs(term.location.x - bound_left)
		t2t = abs(term.location.y - bound_top)
		t2r = abs(term.location.x - bound_right)
		t2b = abs(term.location.y - bound_bottom)
		min_t2e = min([t2l, t2t, t2r, t2b])
		# Horizontal reference
		if (min_t2e == t2t or min_t2e == t2b) and not(h_done): 
			h_ref = term.location.x
			h_done = True
		# Vertical reference
		if (min_t2e == t2l or min_t2e == t2r) and not(v_done): 
			v_ref = term.location.y
			v_done = True
		if h_done and v_done: 
			break
	# pin h/v offset
	h_offset = step
	v_offset = step
	for x in list(range(bound_left, bound_right, step)):
		if abs(x - h_ref) < abs(h_offset): 
			h_offset = h_ref - x
	for y in list(range(bound_bottom, bound_top, step)):
		if abs(y - v_ref) < abs(v_offset):
			v_offset = v_ref - y

	print('offset ---')
	print(step)
	print(h_ref)
	print(v_ref)
	print(h_offset)
	print(v_offset)
	print('---------')
	# Create Position List
	# Origin at LL
	horizontal = []
	vertical = []
	
	#number_of_x_locations = (bound_right - bound_left)/step - 2
	#number_of_y_locations = (bound_top - bound_bottom)/step - 2
	#total_locations = 2* (number_of_x_locations + number_of_y_locations)
	# U1
	#result_x = []
	#result_y = []
	if(macro.box.lowerLeft.x == macro.origin.x and macro.box.lowerLeft.y == macro.origin.y): 
		'''
		for i in range(0, total_locations): 
			if (i==0) :
				x = bound_left +  step 
				y = bound_bottom 
				edge = 0 
			elif(i>=1 and i<number_of_x_locations) :
				x= result_x[i-1] +  step 
				y= bound_bottom 
				edge = 0 
			elif(i== number_of_x_locations) :
				x= bound_right 
				y= bound_bottom+ step 
				edge = 0 
			elif(i< number_of_x_locations+number_of_y_locations) :
				x=bound_right 
				y=result_y[i-1] +  step 
				edge=1 
			elif(i == number_of_x_locations+number_of_y_locations) :
				x=bound_right -  step 
				y=bound_top 
				edge=1 
			elif(i < 2*number_of_x_locations + number_of_y_locations) :
				x=result_x[i-1] -  step 
				y=bound_top 
				edge=2 
			elif(i == 2*number_of_x_locations+ number_of_y_locations) :
				x= bound_left 
				y= bound_top -  step 
				edge=2 
			elif(i<total_locations) :
				x= bound_left 
				y=result_y[i-1] -  step 
				edge=3 
			result_x.append(x+h_offset)
			result_y.append(y+v_offset)
		macro.positionList_x = result_x
		macro.positionList_y = result_y
		'''
		# Bottom edge >
		print('bot')
		for x in list(range(bound_left+pin_pitch, bound_right-pin_pitch, step)): 
			macro.positionList_x.append(x)
			horizontal.append(x)
			macro.positionList_y.append(bound_bottom)
		# Right edge  ^
		for y in list(range(bound_bottom+pin_pitch, bound_top-pin_pitch, step)): 
			macro.positionList_x.append(bound_right)
			vertical.append(y)
			macro.positionList_y.append(y)
		# Top edge   <
		#for x in list(range(bound_right-pin_pitch, bound_left+pin_pitch, -step)) 
		for x in horizontal[::-1]: 
			macro.positionList_x.append(x)
			macro.positionList_y.append(bound_top)
		# Left edge  v
		for y in vertical[::-1]: 
			macro.positionList_x.append(bound_left)
			macro.positionList_y.append(y)
		
	# Origin at LR
	# U0 
	if(macro.box.upperRight.x == macro.origin.x and macro.box.lowerLeft.y == macro.origin.y): 
		'''
		for i in range(0, total_locations) :
			if (i==0) :
				x =bound_right 
				y =bound_bottom + step 
				edge = 0 
			elif(i>=1 and i<number_of_y_locations) :
				x =bound_right 
				y =result_y[i-1]+step 
				edge = 0 
			elif(i== number_of_y_locations) :
				x =bound_right-step 
				y =bound_top 
				edge = 0 
			elif(i< number_of_x_locations+number_of_y_locations) :
				x =result_x[i-1] - step 
				y =bound_top 
				edge=1 
			elif(i == number_of_x_locations+number_of_y_locations) :
				x =bound_left 
				y =bound_top - step 
				edge=1 
			elif(i < 2*number_of_y_locations + number_of_x_locations) :
				x =bound_left 
				y =result_y[i-1] - step 
				edge=2 
			elif(i == 2*number_of_y_locations+ number_of_x_locations) :
				x =bound_left + step 
				y =bound_bottom 
				edge=2 
			elif(i<total_locations) :
				x =result_x[i-1] + step 
				y =bound_bottom 
				edge=3 
			result_x.append(x+h_offset)
			result_y.append(y+v_offset)
		macro.positionList_x = result_x 
		macro.positionList_y = result_y
		'''
		# Right edge  ^
		print('right')
		for y in list(range(bound_bottom+pin_pitch, bound_top-pin_pitch, step)): 
			macro.positionList_x.append(bound_right)
			vertical.append(y)
			macro.positionList_y.append(y)				
		# Top edge   <
		for x in list(range(bound_right-pin_pitch, bound_left+pin_pitch, -step)): 
			macro.positionList_x.append(x)
			horizontal.append(x)
			macro.positionList_y.append(bound_top)
		# Left edge  v
		#for y in list(range(bound_top-pin_pitch, bound_bottom+pin_pitch, -step)): 
		for y in vertical[::-1]:
			macro.positionList_x.append(bound_left)
			macro.positionList_y.append(y)

		# Bottom edge >
		#for x in list(range(bound_left+pin_pitch, bound_right-pin_pitch, step)) :
		for x in horizontal[::-1]: 
			macro.positionList_x.append(x)
			macro.positionList_y.append(bound_bottom)
		
	# Origin at UR
	if(macro.box.upperRight.x == macro.origin.x and macro.box.upperRight.y == macro.origin.y) :
		# Top edge   <
		#print('top')
		for x in list(range(bound_right-pin_pitch, bound_left+pin_pitch, -step)): 
			macro.positionList_x.append(x)
			horizontal.append(x)
			macro.positionList_y.append(bound_top)
		# Left edge  v
		for y in list(range(bound_top-pin_pitch, bound_bottom+pin_pitch, -step)):
			macro.positionList_x.append(bound_left)
			vertical.append(y)
			macro.positionList_y.append(y)

		# Bottom edge >
		#for x in list(range(bound_left+pin_pitch, bound_right-pin_pitch, step)) 
		for x in horizontal[::-1]: 
			macro.positionList_x.append(x)
			macro.positionList_y.append(bound_bottom)
		# Right edge  ^
		#for y in list(range(bound_bottom+pin_pitch, bound_top-pin_pitch, step)) 
		for y in vertical[::-1] :
			macro.positionList_x.append(bound_right)
			macro.positionList_y.append(y)
	# Origin at UL
	if(macro.box.lowerLeft.x == macro.origin.x and macro.box.upperRight.y == macro.origin.y): 
		# Left edge  v
		#print('left')
		for y in list(range(bound_top-pin_pitch, bound_bottom+pin_pitch, -step)): 
			macro.positionList_x.append(bound_left)
			vertical.append(y)
			macro.positionList_y.append(y)
		# Bottom edge >
		for x in list(range(bound_left+pin_pitch, bound_right-pin_pitch, step)): 
			macro.positionList_x.append(x)
			horizontal.append(x)
			macro.positionList_y.append(bound_bottom)
		# Right edge  ^
		#for y in list(range(bound_bottom+pin_pitch, bound_top-pin_pitch, step)) 
		for y in vertical[::-1]: 
			macro.positionList_x.append(bound_right)
			macro.positionList_y.append(y)
		# Top edge   <
		#for x in list(range(bound_right-pin_pitch, bound_left+pin_pitch, -step)) 
		for x in horizontal[::-1]: 
			macro.positionList_x.append(x)
			macro.positionList_y.append(bound_top)	
# ----------------------------------
# non-Cpo version of Solver Helpers
# ----------------------------------
def net_HPWL(net): 
	terms_x = []
	terms_y = []
	for term in net.terms: 
		terms_x.append(term.location.x)
		terms_y.append(term.location.y)
	x_max = max(terms_x)
	x_min = min(terms_x)
	y_max = max(terms_y)
	y_min = min(terms_y)
	return x_max - x_min + y_max - y_min

def t2tDistance(term1, term2): 
	return abs(term1.macro_location.x - term2.macro_location.x) + abs(term1.macro_location.y - term2.macro_location.y)

