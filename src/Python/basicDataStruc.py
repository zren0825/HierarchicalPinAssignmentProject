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
		self.rotated   = False
		def update_macro(self):
			self.perimeter = 2 * (abs(self.box.upperLeft.x - self.box.lowerRight.x)
								+ abs(self.box.upperLeft.y - self.box.lowerRight.y)) 
			self.center.x = abs(self.box.upperLeft.x - self.box.lowerRight.x)/2
			self.center.y = abs(self.box.upperLeft.y - self.box.lowerRight.y)/2 

		def moveTerm(self):
			



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

class Term:
	def __init__(self, name = '', _type = '', location = Location()):
		self.name = name
		self.type = _type
		self.location = location
		self.macro_location = Location()
		self.macro = Macro()
		self.numCopies = 0
		self.edge = ''
		def update_term(self):
			self.macro_location.x = self.location.x - self.macro.center.x
			self.macro_location.y = self.location.y - self.macro.center.y

class Box:
	def __init__(self, upperLeft = Location(), lowerRight = Location()):
		self.upperLeft  = Location()
		#self.upperRight = Location()
		#self.lowerLeft  = Location()
		self.lowerRight = Location()

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

