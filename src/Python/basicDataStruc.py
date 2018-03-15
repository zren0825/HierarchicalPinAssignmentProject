# This file contains definition of basic class/structure
# in the pin assignment task which are expected to be used
# as basic data structures in the CPLEX solver

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
		self.maxPinCopy = 0
		self.box   = Box()
		self.origin = Location()
		self.perimeter = 0 
		self.center = Location()
		self.cpo_center = Location()
		self.rotated   = False

		self.positionList_x = []
		self.positionList_y = []
	def update_macro(self):
		# Updata Perimeter
		self.perimeter = 2 * (self.box.upperRight.x - self.box.lowerLeft.x + self.box.upperRight.y - self.box.lowerLeft.y)
		# Update Center
		self.center.x = int((self.box.upperRight.x + self.box.lowerLeft.x)/2)
		self.center.y = int((self.box.upperRight.y + self.box.lowerLeft.y)/2)

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
	def __init__(self, upperRight = Location(), lowerLeft = Location()):
		self.upperRight  = upperRight

		self.lowerLeft = lowerLeft

class Term:
	def __init__(self, name = '', _type = '', netName = '', location = Location()):
		self.name = name
		self.type = _type
		self.location = location
		self.legal_location = Location()
		self.macro_location = Location()
		self.macro = Macro()
		self.net = Net(netName)
		self.numCopies = 0
		self.edge = ''

		# wrapped  fields
		self.cpo_macro_location = Location()
		self.cpo_location = Location()
		self.cpo_new_location = Location() # for calculating Wmax expression


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

