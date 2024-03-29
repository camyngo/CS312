#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution,
		time spent to find solution, number of permutations tried during search, the
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def greedy( self,time_allowance=60.0 ):
		pass



	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints:
		max queue size, total number of states created, and number of pruned states.</returns>
	'''

	def branchAndBound( self, time_allowance=60.0 ):
        max_queue_size = 0
        num_states = 0
        num_pruned = 0
        num_solutions = 0
        random.seed(time.time())
        results = {}
        self.cities = self._scenario.getCities()
        self.ncities = len(self.cities)
    
        '''Initialize BSSF to the greedy algorithm solution'''
        bssf = self.greedy(time_allowance)['soln']
        # Since the greedy algorithm is quick and provides a good solution, it
        # will provide really early pruning for B&B and improve its efficiency
        # overall. Less states are generated and thus less pruning is needed.
    
        '''Initialize state priority queue'''
        stateQueue = PriorityQueue()
    
        '''	Create the root of the state tree
            Reduce the cost matrix
            Set lower bound to cost of first reduction'''
        root = self.state()
        root.cost_matrix = [[-1 for i in range(self.ncities)] \
                            for k in range(self.ncities)]
        self.initializeState(None, root)
        root.city_num = 0  # Always start at first city
        root.path.append(root.city_num)
        lowerBound = root.cost
    
        stateQueue.put((root.cost, root))
    
        start_time = time.time()
        '''Begin the algorithm'''
        while not stateQueue.empty() \
                and time.time() - start_time < time_allowance:
            if stateQueue.qsize() > max_queue_size:
                max_queue_size = stateQueue.qsize()
            state = stateQueue.get()[1]
            if state.cost > bssf.cost:
                num_pruned += 1
                continue
            '''Make each child state'''
            for j in range(self.ncities):
                if time.time() - start_time > time_allowance:
                    break  # Over on time
                if state.cost_matrix[state.city_num][j] != math.inf:
                    # There is a path from this city to the next
    
                    '''Set up initial values for child'''
                    child = self.state()
                    self.initializeState(state, child, j)
                    num_states += 1
    
                    self.infRowCol(child)
    
                    '''Calculate State Cost'''
                    cost_reduction = self.reduceMatrix(child)
                    cost_step = child.parent.cost_matrix \
                        [child.parent.city_num][child.city_num]
                    cost_prev_state = child.parent.cost
                    child.cost = \
                        cost_prev_state + cost_step + cost_reduction
    
                    '''If the state is a leaf node and
                        it's less than BSSF so far, update
                        BSSF and continue to next state'''
                    if len(child.path) == self.ncities:
                        if child.cost < bssf.cost:
                            '''Make BSSF route'''
                            route = []
                            for i in range(self.ncities):
                                route.append(self.cities[child.path[i]])
                            bssf = TSPSolution(route)
                        num_solutions += 1
                        continue
    
                    '''Add child state to the queue'''
                    if bssf.cost > child.cost > lowerBound:
                        stateQueue.put(((child.cost / child.depth), child))
                        # Encourages digging deeper first
                    else:
                        num_pruned += 1
    
        end_time = time.time()
        results['cost'] = bssf.cost
        results['time'] = end_time - start_time
        results['count'] = num_solutions
        results['soln'] = bssf
        results['max'] = max_queue_size
        results['total'] = num_states
        results['pruned'] = num_pruned
        return results


def initializeState(self, parent, child, j=0):
    if parent == None:
        # This is the root of the state tree, or state one
        root = child
        root.city_num = 0
        # first state assumes always starting at first city
        root.depth = 1
        '''Initialize first state cost matrix'''
        for i in range(self.ncities):
            for k in range(self.ncities):
                root.cost_matrix[i][k] = self.cities[i].costTo(
                    self.cities[k])
        '''Reduce the cost matrix'''
        root.cost = self.reduceMatrix(root)
    else:
        # This is a child state
        child.parent = parent
        child.city_num = j
        child.depth = child.parent.depth + 1
        # Don't want the parent values to be overwritten so
        # make a deep copy
        child.cost_matrix = \
            copy.deepcopy(child.parent.cost_matrix)
        child.path = copy.deepcopy(child.parent.path)
        child.path.append(j)


'''O(3n) ~= o(n)'''


def infRowCol(self, state):
    '''Inf out appropriate row and column'''
    row = state.parent.city_num
    col = state.city_num
    for k in range(self.ncities):
        state.cost_matrix[row][k] = math.inf
    for k in range(self.ncities):
        state.cost_matrix[k][col] = math.inf

    '''Prevent premature cycles'''
    path_len = len(state.path)
    index = path_len - 1
    while index >= 0:
        row = state.city_num
        col = state.path[index]
        state.cost_matrix[row][col] = math.inf
        index -= 1


def reduceMatrix(self, state):
    total_cost = 0
    '''Reduce row-by-row'''
    '''O(n^2)'''
    for i in range(self.ncities):
        row_min = math.inf
        '''Find the minimum value in the row'''
        for j in range(self.ncities):
            if state.cost_matrix[i][j] < row_min:
                row_min = state.cost_matrix[i][j]

        '''Subtract minimum value from each position in row'''
        if row_min != math.inf and row_min != 0:
            total_cost += row_min
            for j in range(self.ncities):
                state.cost_matrix[i][j] -= row_min

    '''Reduce column by column'''
    for j in range(self.ncities):
        col_min = math.inf
        '''Find the minimum value in the column'''
        for i in range(self.ncities):
            if state.cost_matrix[i][j] < col_min:
                col_min = state.cost_matrix[i][j]

        '''Subtract minimum value from each position in column'''
        if col_min != math.inf and col_min != 0:
            total_cost += col_min
            for i in range(self.ncities):
                state.cost_matrix[i][j] -= col_min

    return total_cost

    ''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found during search, the
		best solution found.  You may use the other three field however you like.
		algorithm</returns>
	'''

	def fancy( self,time_allowance=60.0 ):
		pass
