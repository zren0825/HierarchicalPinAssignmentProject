import re
import pdb
import os

class Graph:
	def __init__(self,name=''):
		self.name = name
		self.sources = []
		self.sinks = []
		self.nodehash = {} #(key,value) = (name, node)
		self.edges = []
		self.nodes = []
		self.topological_sort = None

	def printOutDot(self,filename='out.dot'):
		dotStr = ''
		dotStr = dotStr + "digraph G{\n"
		dotStr = dotStr + "\tnode [fontcolor=white,style=filled,color=blue2];\n"
		for node in self.nodes:
			dotStr = dotStr + "\t{node} [label = {name}];\n".format(node=node.name,name=node.name)
		for edge in self.edges:
			dotStr = dotStr + "\t{head} -> {tail};\n".format(head=edge.head.name,tail=edge.tail.name)
		
		dotStr = dotStr + '}\n'

		write2file(filename=filename,content=dotStr)

		comm = "dot -Tps {dotfile} -o {psfile}".format(dotfile=filename,psfile=filename+'.ps')
		os.system(comm)

		rmdot="rm {dotfile}".format(dotfile=filename)
		os.system(rmdot)

	def addNode(self,name=''):
		if name in self.nodehash.keys():
			return self.nodehash[name]
		else:
			newNode = Node(name=name)
			self.nodehash[name] = newNode
			self.nodes.append(newNode)
			return newNode
	
	def createEdge(self,head=None,tail=None,name=''):
		if head==None or tail==None:
			print("head or tail does not exist in the graph")
			pdb.set_trace()
		edgename = name
		if name=='':
			edgename = head.name + "TO" + tail.name
		newEdge = Edge(name=edgename,head=head,tail=tail)
		head.going_out_edges.append(newEdge)
		tail.coming_in_edges.append(newEdge)
		self.edges.append(newEdge)
		return newEdge

	def findEdge(self,head=None,tail=None):
		for edge in head.going_out_edges:
			if edge.tail == tail:
				return edge
		return None

	def findNode(self,name):
		for node in self.nodes:
			if node.name == name:
				return node
		return None

	def deleteEdge(self,edge):
		head=edge.head
		tail=edge.tail
		if head:
			head.going_out_edges.remove(edge)
		if tail:
			tail.coming_in_edges.remove(edge)
		if edge in self.edges:
			self.edges.remove(edge)

	def deleteNode(self,name):
		if self.findNode(name):
			node = self.nodehash[name]
			self.connectHeadTail(node)
			self.deleteNodeEdge(node)
			del self.nodehash[name]
			self.nodes.remove(node)
		else:
			print("node {n} is not in graph {gn}".format(n=name,gn=self.name))

	
	def getSourceSink(self):
		self.sinks=[]
		self.sources=[]
		for node in self.nodes:
			if not node.going_out_edges:
				self.sinks.append(node)
			if not node.coming_in_edges:
				self.sources.append(node)

	def topologicalSort(self,source2sink=True):
		### if source2sink is true, topological sort is done through sources to sinks
		### otherwise, topological sort is done through sinks to sources

		topological_sort = {} #(key,value)=(level,a list of nodes in that level)
		topological_sources = []

		self.getSourceSink()

		visited_nodes = []
		if source2sink:
			topological_sources.extend(self.sources)
		else:
			topological_sources.extend(self.sinks)

		topological_sort[1] = []
		for source in topological_sources:
			topological_sort[1].append(source)
			visited_nodes.append(source)

		level = 1
		while(True):
			current_level = topological_sort[level]
			next_level = []
			level = level + 1
			for node in current_level:
				topological_next_level_nodes = []
				topological_predecessors = {}
				if source2sink:
					for edge in node.going_out_edges:
						if not edge.tail in topological_next_level_nodes:
							topological_next_level_nodes.append(edge.tail)
							topological_predecessors[edge.tail] = []
						for tailedge in edge.tail.coming_in_edges:
							if not tailedge.head in topological_predecessors[edge.tail]:
								topological_predecessors[edge.tail].append(tailedge.head)
				else:
					for edge in node.coming_in_edges:
						if not edge.head in topological_next_level_nodes:
							topological_next_level_nodes.append(edge.head)
							topological_predecessors[edge.head] = []
						for headedge in edge.head.going_out_edges:
							if not headedge.tail in topological_predecessors[edge.head]:
								topological_predecessors[edge.head].append(headedge.tail)

				for nextlevelnode in topological_next_level_nodes:
					predecessors_done =True
					for predecessor in topological_predecessors[nextlevelnode]:
						if not predecessor in visited_nodes:
							predecessors_done = False
							break
					if predecessors_done:
						if not nextlevelnode in next_level:
							next_level.append(nextlevelnode)

			if next_level:
				topological_sort[level] = []
				topological_sort[level].extend(next_level)
				visited_nodes.extend(next_level)
			else:
				break

		self.topological_sort=topological_sort
		return topological_sort

	def printTopologicalLevel(self):
		for (k,v) in self.topological_sort.items():
			print("level : {l}".format(l=k))
			nodestr ='\t'
			for node in v:
				nodestr = nodestr + " "+node.name
			print nodestr

class Node:
	def __init__(self,name=''):
		self.name = name
		self.coming_in_edges = []
		self.going_out_edges = []

		self.assigned_resource = None
		self.start_time = 0
		self.asap = 1
		self.alap = 15

class Edge:
	def __init__(self,name='',head=None,tail=None):
		self.name = name
		self.head = head
		self.tail = tail

class ResourceLibrary:
	def __init__(self,name=''):
		self.resources=[]
		self.name=name
		self.resourcehash={}

class Resource:
	def __init__(self,name='',latency=0,number=0,area=0):
		self.name=name
		self.latency=latency
		self.number=number
		self.area = area

class CostTable:
	def __init__(self,name=''):
		self.name=name
		self.nodes = []
		self.resources = []

		self.nodeRes_table = {} # key=node, value = a list of resources that can execute that node

		self.res_nodes = {} #key=resource, value = a list of nodes that can be executed by the resource

	def printCostTable(self):
		for (node,reses) in self.nodeRes_table.items():
			print node.name + " : ",
			resstr=''
			for res in reses:
				resstr=resstr + res.name+" "
			print resstr

def write2file(filename='',content=''):
	f=None
	if filename == '':
		f=sys.stdout
	else:
		f=open(filename,'w')
	
	f.write(content+"\n")

	if filename != '':
		f.close()
