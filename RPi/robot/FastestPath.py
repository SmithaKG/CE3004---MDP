#!/usr/bin/env python
"""Implementation of the fastest path algorithm for maze solving robot."""
import copy
import numpy as np

from Constants import MAX_ROWS, MAX_COLS, NORTH, SOUTH, EAST, WEST, FORWARD, LEFT, RIGHT


class Node:
    """To create nodes of a graph.

    Attributes:
        coord (tuple): The (row, col) coordinate
        G (int): The cost to reach this node
        H (int): The cost to goal node
        parent (Node): The parent of this node
        value (int): The value at this location in exploration map

    """

    def __init__(self, value, coord, H):
        """To initialize an instance of Node class.

        Args:
            value (int): The value of the node
            coord (tuple): The (row, col) coordinate
            H (int): The cost to goal node

        """
        self.value = value
        self.coord = coord
        self.parent = None
        self.H = H
        self.G = float('inf')


class FastestPath:
    """Implementation of the A* algorithm to find the fastest path in a 2D maze.

    Attributes:
        exploredMap (Numpy array): The map after the exploration stage
        goal (list): Coordinate of the goal cell
        graph (list): To form the fastest path graph
        index (int): Counter
        path (list): The fastest path
        robot (Robot): Instance of the Robot class
        start (list): Coordinate of the initial cell
        waypoint (list): Coordinate of the way-point if specified

    """

    def __init__(self, exploredMap, start, goal, direction, waypoint=None, calibrateLim=5, sim=False):
        """To initialize an instance of the FastestPath class.

        Args:
            exploredMap (Numpy array): The map after the exploration stage
            start (list): Coordinate of the initial cell
            goal (list): Coordinate of the goal cell
            direction (int): The starting direction of the robot
            waypoint (list, optional): Coordinate of the way-point if specified
            sim (bool, optional): To specify the run is simulation or real mode

        """
        self.exploredMap = exploredMap
        self.graph = []
        self.start = start
        self.goal = goal
        self.waypoint = waypoint
        self.index = 1
        self.direction = direction
        self.path = []
        self.movement = []
        self.calibrateLim = calibrateLim
        self.sim = sim

        if sim:
            from Simulator import Robot
            self.robot = Robot(self.exploredMap, direction, start, None)
        if not sim:
            from Real import Robot
            self.robot = Robot(self.exploredMap, direction, start)

    def __initGraph(self, h_n):
        """To create a grid of graph nodes from the exploration map.

        Args:
            h_n (Numpy array): The heuristic cost of each node to goal node

        """
        self.graph = []
        for row in xrange(MAX_ROWS):
            self.graph.append([])
            for col in xrange(MAX_COLS):
                self.graph[row].append(Node(self.exploredMap[row][col], (row, col), h_n[row][col]))

    def __validInds(self, inds):
        """To check if the input indices are valid or not.

        To be valid the following conditions must be met:
            * A 3x3 neighbourhood around the center should lie within the arena
            * A 3x3 neighbourhood around the center should have no obstacle

        Args:
            inds (list of list): List of coordinates to be checked

        Returns:
            list of list: All indices that were valid

        """
        valid = []

        for i in inds:
            r, c = i
            x, y = np.meshgrid([-1, 0, 1], [-1, 0, 1])
            x, y = x+r, y+c
            if (np.any(x < 0) or np.any(y < 0) or np.any(x >= MAX_ROWS)
               or np.any(y >= MAX_COLS)):
                valid.append(False)
            elif (np.any(self.exploredMap[x[0, 0]:x[0, 2]+1, y[0, 0]:y[2, 0]+1] != 1)):
                valid.append(False)
            else:
                valid.append(True)

        return [inds[i] for i in range(len(inds)) if valid[i]]

    def __astar(self, start, goal):
        """To implement the a* algorithm to find the fastest path in a 2d maze.

        Args:
            start (list): Coordinates of the starting cell
            goal (list): Coordinates of the goal cell

        Returns:
            list of list: List of coordinates of the path from start to goal

        Raises:
            ValueError: If no path is found between the given start and goal

        """
        goal = self.graph[goal[0]][goal[1]]

        # set of nodes already evaluated
        closedSet = set()

        # set of discovered nodes that have not been evaluated yet
        openSet = set()

        current = self.graph[start[0]][start[1]]
        current.G = 0

        # add start node to openSet
        openSet.add(current)

        prev = None

        while (openSet):
            key1 = lambda o: o.G + o.H
            current = min(openSet, key=key1)

            if prev:
                self.__setDirection(prev.coord, current.coord)

            # if goal is reached trace back the path
            if (current == goal):
                path = []

                while (current.parent):
                    path.append(current.coord)
                    current = current.parent

                path.append(current.coord)

                return path[::-1]
            else:
                openSet.remove(current)
                closedSet.add(current)

                for node in self.__getNeighbours(current):
                    if node in closedSet:
                        continue

                    if node in openSet:
                        # calculate new G cost
                        tempCost = self.__getCost(current.coord, node.coord)
                        new_g = current.G + tempCost
                        if node.G > new_g:
                            node.G = new_g
                            node.parent = current
                    else:
                        # if neither in openSet nor in closedSet
                        # cost of moving between neighbours is 1
                        tempCost2 = self.__getCost(current.coord, node.coord)
                        node.G = current.G + tempCost2
                        node.parent = current
                        openSet.add(node)

            prev = copy.deepcopy(current)

        # exception is no path is found
        raise ValueError('No Path Found')

    def __getHeuristicCosts(self, goal):
        """Calculate the Manhattan distance between each cell and the goal cell.

        Args:
            goal (list): Coordinates of the goal cell

        Returns:
            Numpy array: 2D grid with each cell storing the distance to goal

        """
        # this will create a grid of coordinates
        cols, rows = np.meshgrid(range(0, 15), range(0, 20))
        cost = np.zeros([20, 15])
        temp1 = np.square(rows - goal[0])
        temp2 = np.square(cols - goal[1])
        cost = np.sqrt(temp1 + temp2)
        cost /= np.max(cost)

        return cost

    def __getNeighbours(self, loc):
        """Return the coordinates of a 3x3 neighbourhood around the input location.

        Only neighbours that have been explored and not obstacles are returned

        Args:
            loc (list): Coordinates of a cell

        Returns:
            list of list: Coordinates of all valid neighbours of the cell

        """
        r, c = loc.coord
        inds = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        inds = self.__validInds(inds)
        neighbours = [self.graph[n[0]][n[1]] for n in inds]

        # if its explored and not an obstacle
        return [n for n in neighbours if n.value == 1]

    def __getCost(self, current_pos, next_pos):
        """Calculate the cost to move one node.

        Args:
            current_pos (list): Coordinates of the current position
            next_pos (list): Coordinates of the next position

        Returns:
            int: Cost of the move

        """
        if self.direction in [NORTH, SOUTH]:
            if current_pos[1] == next_pos[1]:
                return 0
            else:
                return 1
        else:
            if current_pos[0] == next_pos[0]:
                return 0
            else:
                return 1

        return 1

    def __setDirection(self, prev_pos, current_pos):
        """Set the direction of the robot after moving.

        Args:
            prev_pos (list): Coordinates of the previous position
            current_pos (list): Coordinates of the current position

        """
        if prev_pos[0] < current_pos[0]:
            self.direction = SOUTH
        elif prev_pos[1] < current_pos[1]:
            self.direction = EAST
        elif prev_pos[1] > current_pos[1]:
            self.direction = WEST
        else:
            self.direction = NORTH

    def fastestPathRun(self):
        """To simulate the fastest path run.

        Returns:
            movement (list): List of movements from start to goal

        """
        print "Fastest Path Mode started!"
        self.getFastestPath()
        while (self.robot.center.tolist() != self.goal):
            self.moveStep()
        print "Fastest Path completed!"
        return self.movement

    def getFastestPath(self):
        """To calculate the fastest path and handle a way-point input."""
        path = []
        start = copy.copy(self.start)

        if (self.waypoint):
            h_n = self.__getHeuristicCosts(self.waypoint)
            self.__initGraph(h_n)
            fsp = self.__astar(start, self.waypoint)
            start = copy.copy(self.waypoint)

            # Leave out last element as it is the start for next fastest path
            # (Otherwise the way-point will be added twice)
            path.extend(fsp[:-1])

        h_n = self.__getHeuristicCosts(self.goal)
        self.__initGraph(h_n)
        fsp = self.__astar(start, self.goal)
        path.extend(fsp)
        self.path = path
        self.markMap()

    def markMap(self):
        """To mark the path on the exploration map."""
        for ind in self.path:
            self.exploredMap[tuple(ind)] = 6

    def moveStep(self):
        """To determine the next move for the robot to follow the path.

        Inputs the fastest path and the robot location

        """
        movement = []

        if (self.robot.center.tolist() != self.path[self.index]):
            diff = self.robot.center - np.asarray(self.path[self.index])

            if (diff[0] == -1 and diff[1] == 0):  # Going south
                if self.robot.direction == NORTH:
                    movement.extend((RIGHT, RIGHT, FORWARD))
                elif self.robot.direction == EAST:
                    movement.extend((RIGHT, FORWARD))
                elif self.robot.direction == SOUTH:
                    movement.append(FORWARD)
                else:
                    movement.extend((LEFT, FORWARD))
            elif (diff[0] == 0 and diff[1] == 1):  # Going west
                if self.robot.direction == NORTH:
                    movement.extend((LEFT, FORWARD))
                elif self.robot.direction == EAST:
                    movement.extend((RIGHT, RIGHT, FORWARD))
                elif self.robot.direction == SOUTH:
                    movement.extend((RIGHT, FORWARD))
                else:
                    movement.append(FORWARD)
            elif (diff[0] == 0 and diff[1] == -1):  # Going east
                if self.robot.direction == NORTH:
                    movement.extend((RIGHT, FORWARD))
                elif self.robot.direction == EAST:
                    movement.append(FORWARD)
                elif self.robot.direction == SOUTH:
                    movement.extend((LEFT, FORWARD))
                else:
                    movement.extend((RIGHT, RIGHT, FORWARD))
            else:  # Going north
                if self.robot.direction == NORTH:
                    movement.append(FORWARD)
                elif self.robot.direction == EAST:
                    movement.extend((LEFT, FORWARD))
                elif self.robot.direction == SOUTH:
                    movement.extend((RIGHT, RIGHT, FORWARD))
                else:
                    movement.extend((RIGHT, FORWARD))

            for move in movement:
                self.robot.moveBot(move)

        self.movement.extend(movement)
        # if not (self.sim):
        #     if (self.robot.stepCounter + len(movement) > self.calibrateLim):
        #         calibrate = self.robot.can_calibrate()
        #         if (calibrate[0]):
        #             movement.append(calibrate[1])
        #             self.robot.stepCounter = 0
        self.index += 1
