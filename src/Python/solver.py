# This file contains implemention of CPLEX solver
# in the pin assignment task which are expected to be used
# as the main function in the CPLEX solver
# Last modified: 03/07/2018 3PM 

from docplex.cp.model import CpoModel
from itertools import groupby
import basicDataStruc as ds
import utils
import helpers

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
macroNetFile = 'simple_test_v0.txt'
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
[macro_types, unique_macros] = helpers.findUniqueMacros(macros)
# Process macro term location to macro-reference-location
unique_macros = helpers.processMacroTermLocation(unique_macros)


# --------------------
#  Build Model
# --------------------

# Create Model
pin_assignment_model = CpoModel()
# Create Variables
macro_vars = []
for macro in unique_macros:
	macro_var = pin_assignment_model.integer_var_list(len(macro.terms), 0, int(macro.perimeter/min_pitch), macro.type)
	macro_vars.append(macro_var)
# TODO: Rotation and Multi-copies

# Add Constraints

# Add Objective




# --------------------
#  Solve and display
# --------------------