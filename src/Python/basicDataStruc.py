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
		self.rotated   = False
		def update_perimeter(self):
			self.perimeter = 2 * (abs(self.box.upperLeft - self.box.upperRight)
								+ abs(self.box.upperLeft - self.box.lowerRight)) 
		def rotate(self):
			self.rotated = True
			#TODO: rotate
		def addPinCopy(self):
			self.maxPinCopy += 1
			#TODO: rotate
		def removeCopy(self):
			self.maxPinCopy 
class Net:
	def __init__(self, name=''):
		self.name = name
		self.terms = []
		self.wireLength = 0

class Pin:
	def __init__(self, location = Location()):
		self.name = name
		self.location = location
		self.numCopies = 0
		self.edge = ''

class Box:
	def __init__(self, upperLeft = 0, upperRight = 0, lowerLeft = 0, lowerRight = 0):
		self.upperLeft  = Location()
		self.upperRight = Location()
		self.lowerLeft  = Location()
		self.lowerRight = Location()

class Location:
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

class PerformanceMetrics:
	def __init__(self, name = '', Wmax = 0, Wmn = 0, p = 0, m = 0)
		self.name = name
		self.Wmax = Wmax
		self.Wmn  = Wmn
		self.p    = p
		self.m    = m
		#self.e   = e
	def Score(self):
		return 1*Wmax + 2*Wmn + 2*p + 2*m # + 3*e

