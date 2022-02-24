from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		points = self.sort_points(points)
		t2 = time.time()

		t3 = time.time()
		hull = self.get_hull(points)
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		polygon = []
		polygon.append(QLineF(hull.first.p, hull.first.next.p))
		node = hull.first.next
		while node is not hull.first:
			polygon.append(QLineF(node.p, node.next.p))
			node = node.next

		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	#sorts a list/array of points by ascending x-value
	#runs in O(n*log(n)) time
	def sort_points(self, points):
		if len(points) == 1:
			return points			#a list of length one is sorted
		
		a = points[:len(points)//2]	#split into two lists
		b = points[len(points)//2:]

		a = self.sort_points(a)		#recursively sort the lists
		b = self.sort_points(b)		#which happens log(n) times

		index_a = 0
		index_b = 0
		final = []

		while(True):								#iterate through both lists
			if a[index_a].x() < b[index_b].x():		#compare the two values, and append the
				final.append(a[index_a])			#lesser value to the new list
				index_a += 1						#then move to the next item in the list
				if index_a >= len(a):				#this will take n time
					final.extend(b[index_b:])
					return final
			
			else:
				final.append(b[index_b])
				index_b += 1
				if index_b >= len(b):
					final.extend(a[index_a:])
					return final


	#the recursive function that calculates the convex hull of the
	#sorted list of points
	#runs in O(n*log(n)) time
	def get_hull(self, points):
		if len(points) <= 3:
			hull = Hull(points)
			return hull					#create a hull from these points

		a = points[:len(points)//2]		#split the list of points
		b = points[len(points)//2:]
		
		a = self.get_hull(a)					#recursively make hull
		b = self.get_hull(b)					#this is takes log(n) time

		right_a = a.rightMost
		first_b = b.first

		pair1 = self.merge_top(right_a, first_b)	#these two lines together take at
		pair2 = self.merge_bottom(right_a, first_b)	#most n time

		pair1[0].append_after(pair1[1])		#this is what actually connects the two
		pair2[0].append_after(pair2[1])		#hulls based on the results of the merges

		a.rightMost = b.rightMost			#updating which node has the highest x-value
		return a

	#finds the upper tangent between two hulls, and returns
	#the points that form that tangent
	#runs in O(n) time
	def merge_top(self, p1, p2):

		s1 = get_slope(p1.p, p2.p)			#find the slope from p1 to p2
		s2 = get_slope(p1.prev.p, p2.p)		#and from the next point up from p1 to p2

		while s2 < s1:							#so long as the slope is decreasing
			p1 = p1.prev						#keep moving up the left hull
			s1 = s2
			s2 = get_slope(p1.prev.p, p2.p)

		s2 = get_slope(p1.p, p2.next.p)		#then start moving up the right hull
		if s2 <= s1:			#if the first "move" decreases the slope, then
			return(p1, p2)		#we have found the tangent
		while s2 > s1:						#otherwise keep moving up the right hull
			p2 = p2.next					#until the slope stops increasing
			s1 = s2
			s2 = get_slope(p1.p, p2.next.p)

		return self.merge_top(p1, p2)		#repeat until the tangent is found

	#find the lower tangent between two hulls, and returns
	#the points that form that tangent
	#uses the same method as merge_top, but moves down the hulls instead of up
	#runs in O(n) time
	def merge_bottom(self, p1, p2):

		s1 = get_slope(p1.p, p2.p)
		s2 = get_slope(p1.next.p, p2.p)

		while s2 > s1:
			p1 = p1.next
			s1 = s2
			s2 = get_slope(p1.next.p, p2.p)

		s2 = get_slope(p1.p, p2.prev.p)
		if s2 >= s1:
			return(p2, p1)
		while s2 < s1:
			p2 = p2.prev
			s1 = s2
			s2 = get_slope(p1.p, p2.prev.p)

		return self.merge_bottom(p1, p2)

class Hull:
	#this class defines a hull as a circular linked list of points
	#and keeps track of important values needed to merge two hulls
	#as part of the convex hull calculation

	def __init__(self, points):				#creating a base hull from either 2 or 3 sorted points
		self.first = Node(points[0])		#the first point will always also
		self.rightMost = None				#be the first in the hull

		if len(points) == 2:				#with only two points, the second point in the list
			node = Node(points[1])			#is also the second point in the hull
			self.first.append_after(node)

			node.next = self.first			#this is a circular linked list
			self.first.prev = node

			self.rightMost = node			#keeping track of the node with the highest x-value
		else:
			slope_a = get_slope(points[0], points[1])	#the point that results in the
			slope_b = get_slope(points[0], points[2])	#greater slope goes next in the hull
			if slope_a > slope_b:
				node = self.first.append_after(Node(points[1]))
				x1 = node.p.x()

				node = node.append_after(Node(points[2]))
				x2 = node.p.x()

				if x1 > x2:								#whichever node has the higher x-value
					self.rightMost = node.prev			#is the right-most node
				else:
					self.rightMost = node
				node.next = self.first		#making the list circular
				self.first.prev = node
			else:
				node = self.first.append_after(Node(points[2]))
				x1 = node.p.x()

				node = node.append_after(Node(points[1]))
				x2 = node.p.x()

				if x1 > x2:							#whichever node has the higher x-value
					self.rightMost = node.prev		#is the right-most node
				else:
					self.rightMost = node
				node.next = self.first		#making the list circular
				self.first.prev = node


#returns the slope of the line created by two points
def get_slope(a, b):
	y = b.y() - a.y()
	x = b.x() - a.x()
	if x == 0:
		return -1
	return y/x

#simple class for keeping track of the linked list of
#points in the hull. a linked list allows for inserts
#and other edits to the list to be done in constant time
class Node:

	def __init__(self, point):
		self.p = point
		self.next = None
		self.prev = None

	def append_after(self, node):
		self.next = node
		node.prev = self
		return node