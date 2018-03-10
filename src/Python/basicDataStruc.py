# This file contains definition of basic class/structure
# in the pin assignment task which are expected to be used
# as basic data structures in the CPLEX solver
# Last modified: 03/07/2018 2PM 
class Block:
	def __init__(self, name=''):
		self.name   = name
		self.macros = []
		self.nets   = []

class Macro:
	def __init__(self, name=''):
		self.name  = name
		self.type  = ''
		self.terms = []
		self.pins  = []
		self.maxPinCopy = 0
		self.box   = Box()
		self.perimeter = 0 
		self.center = Location()
		self.cpo_center = 
		self.rotated   = False
	def update_macro(self):
		# Updata Perimeter
		self.perimeter = 2 * (self.box.lowerRight.x - self.box.upperLeft.x + self.box.upperLeft.y - self.box.lowerRight.y)
		# Update Center
		self.center.x = int((self.box.upperLeft.x + self.box.lowerRight.x)/2)
		self.center.y = int((self.box.upperLeft.y + self.box.lowerRight.y)/2)

	def rotate(self):
		self.rotated = True
		#TODO: rotate
	def addPinCopy(self):
		self.maxPinCopy += 1
		#TODO: addPin
	def removeCopy(self):
		self.maxPinCopy -= 1
		#TODO:removePin
class Net:
	def __init__(self, name=''):
		self.name = name
		self.terms = []
		#self.wireLength = 0

class Location:
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

class Box:
	def __init__(self, upperLeft = Location(), lowerRight = Location()):
		self.upperLeft  = upperLeft
		#self.upperRight = Location()
		#self.lowerLeft  = Location()
		self.lowerRight = lowerRight

class Term:
	def __init__(self, name = '', _type = '', netName = '', location = Location()):
		self.name = name
		self.type = _type
		self.location = location
		self.macro_location = Location()
		self.macro = Macro()
		self.net = Net(netName)
		self.numCopies = 0
		self.edge = ''
		self.pointList_x = []
		self.pointList_y = []
		# wrapped  fields
		self.cpo_macro_location = Location()
		self.cpo_location = Location()

	def update_term(self):
		# Update macro-reference location
		self.macro_location = Location(self.location.x - self.macro.center.x,self.location.y - self.macro.center.y)
		# Update edge
		"""
		macro_width  = abs(self.macro.box.upperLeft.x - self.macro.box.lowerRight.x)
		macro_height = abs(self.macro.box.upperLeft.y - self.macro.box.lowerRight.y)
		if(self.macro_location.x == macro_width/2):
			self.edge = 'right'
		elif(self.macro_location.x == -macro_width/2):
			self.edge = 'left'
		elif (self.macro_location.y == macro_height/2):
			self.edge = 'top'
		else:
			self.edge = 'bottom'
		"""
		# used in helpers.moveTerm()
	def update_location(self):
		self.location = Location(self.macro.center.x + self.macro_location.x,self.macro.center.y + self.macro_location.y)

class PerformanceMetrics:
	def __init__(self, name = '', Wmax = 0, Wmn = 0, p = 0, m = 0):
		self.name = name
		self.Wmax = Wmax
		self.Wmn  = Wmn
		self.p    = p
		self.m    = m
		#self.e   = e
	def Score(self):
		return 1*Wmax + 2*Wmn + 2*p + 2*m # + 3*e

