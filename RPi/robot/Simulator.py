#!/usr/bin/env python
"""Implementation of the Robot class for simulation mode.
"""
import numpy as np
import os

from Constants import MAX_ROWS, MAX_COLS, NORTH, SOUTH, EAST, WEST, RIGHT, LEFT


class Robot:

    """Robot class keeps track of the current location and direction of the robot,
       gets values from the distance sensors and sends commands to move the robot

    Attributes:
        center (list): Center location of the robot
        direction (int): Current direction of the robot (see Constants)
        exploredMap (Numpy array): The current explored map
        head (list): Location of the head of the robot
        map (Numpy array): Real map of the arena for simulation mode
        movement (string): The latest movement of the robot (see Constants)
        realMap (string): File name for map
    """

    def __init__(self, exploredMap, direction, start, realMap):
        """Constructor to initialise an instance of the Exploration class

        Args:
            exploredMap (Numpy array): To initial state of the exploration map
            direction (int): The starting direction for the robot (see Constants)
            start (list): The starting center location of the robot
            realMap (string): File name of the real map
        """
        self.exploredMap = exploredMap
        self.direction = direction
        self.center = np.asarray(start)
        self.head = None
        self.setHead()
        if realMap:
            self.realMap = realMap
            self.map = self.loadMap()
        self.movement = []
        self.markArea(start, 1)

    def markArea(self, center, value):
        """To mark a 3x3 neighbourhood around the center location with a particular
           value

        Args:
            center (list): Location to mark neighbourhood around
            value (int): The value to be filled
        """
        self.exploredMap[center[0]-1:center[0]+2, center[1]-1:center[1]+2] = value

    def setHead(self):
        if (self.direction == NORTH):
            self.head = self.center + [-1, 0]
        elif (self.direction == EAST):
            self.head = self.center + [0, 1]
        elif (self.direction == SOUTH):
            self.head = self.center + [1, 0]
        else:
            self.head = self.center + [0, -1]

    def loadMap(self):
        """To load the real map file and store it as a Numpy array

        Returns:
            Numpy array: Real map
        """
        with open(os.path.join('Maps', self.realMap)) as f:
            return np.genfromtxt(f, dtype=int, delimiter=1)

    def getValue(self, inds):
        """To get sensor values (from the real map for simulation) at the given indices

        Args:
            inds (list of list): Indices to get sensor values at

        Returns:
            list: values of the sensors and puts none after the first obstacle is encountered
        """
        vals = []
        for (r, c) in inds:
            if (0 <= r < MAX_ROWS) and (0 <= c < MAX_COLS):
                if self.map[r][c] == 2:
                    if self.exploredMap[r][c] == 0:
                        self.exploredMap[r][c] = 2
                    vals.append(2)
                    break
                else:
                    if self.exploredMap[r][c] == 0:
                        self.exploredMap[r][c] = 1
                    vals.append(1)
        if len(vals) < len(inds):
            vals = vals + [None]*(len(inds)-len(vals))
        return vals

    def getSensors(self):
        """Generated indices to get values from sensors and gets the values using getValue() function.
           For this simulator it is assumed that the sensors can get values up a distance of 4 cells

        Returns:
            Numpy array of Numpy arrays: Sensor values from all sensors
        """
        distanceSuperShort = 2
        distanceShort = 3
        distanceLong = 5
        r, c = self.center
        # sensor_vals = [FL_SR, FC_US, FR_SR, RT_SR, RM_SR, LT_LR, LM_LR]

        # Front Left
        if self.direction == NORTH:
            self.getValue(zip(range(r-distanceShort-1, r-1), [c-1]*distanceShort)[::-1])
        elif self.direction == EAST:
            self.getValue(zip([r-1]*distanceShort, range(c+2, c+distanceShort+2)))
        elif self.direction == WEST:
            self.getValue(zip([r+1]*distanceShort, range(c-distanceShort-1, c-1))[::-1])
        else:
            self.getValue(zip(range(r+2, r+distanceShort+2), [c+1]*distanceShort))

        # Front Center
        if self.direction == NORTH:
            self.getValue(zip(range(r-distanceShort-1, r-1), [c]*distanceShort)[::-1])
        elif self.direction == EAST:
            self.getValue(zip([r]*distanceShort, range(c+2, c+distanceShort+2)))
        elif self.direction == WEST:
            self.getValue(zip([r]*distanceShort, range(c-distanceShort-1, c-1))[::-1])
        else:
            self.getValue(zip(range(r+2, r+distanceShort+2), [c]*distanceShort))

        # Front Right
        if self.direction == NORTH:
            self.getValue(zip(range(r-distanceShort-1, r-1), [c+1]*distanceShort)[::-1])
        elif self.direction == EAST:
            self.getValue(zip([r+1]*distanceShort, range(c+2, c+distanceShort+2)))
        elif self.direction == WEST:
            self.getValue(zip([r-1]*distanceShort, range(c-distanceShort-1, c-1))[::-1])
        else:
            self.getValue(zip(range(r+2, r+distanceShort+2), [c-1]*distanceShort))

        # Right Top
        if self.direction == NORTH:
            self.getValue(zip([r-1]*distanceSuperShort, range(c+2, c+distanceSuperShort+2)))
        elif self.direction == EAST:
            self.getValue(zip(range(r+2, r+distanceSuperShort+2), [c+1]*distanceSuperShort))
        elif self.direction == WEST:
            self.getValue(zip(range(r-distanceSuperShort-1, r-1), [c-1]*distanceSuperShort)[::-1])
        else:
            self.getValue(zip([r+1]*distanceSuperShort, range(c-distanceSuperShort-1, c-1))[::-1])

        # Right Middle
        if self.direction == NORTH:
            self.getValue(zip([r]*distanceSuperShort, range(c+2, c+distanceSuperShort+2)))
        elif self.direction == EAST:
            self.getValue(zip(range(r+2, r+distanceSuperShort+2), [c]*distanceSuperShort))
        elif self.direction == WEST:
            self.getValue(zip(range(r-distanceSuperShort-1, r-1), [c]*distanceSuperShort)[::-1])
        else:
            self.getValue(zip([r]*distanceSuperShort, range(c-distanceSuperShort-1, c-1))[::-1])

        # Left Top
        if self.direction == NORTH:
            self.getValue(zip([r-1]*distanceLong, range(c-distanceLong-1, c-1))[::-1])
        elif self.direction == EAST:
            self.getValue(zip(range(r-distanceLong-1, r-1), [c+1]*distanceLong)[::-1])
        elif self.direction == WEST:
            self.getValue(zip(range(r+2, r+distanceLong+2), [c-1]*distanceLong))
        else:
            self.getValue(zip([r+1]*distanceLong, range(c+2, c+distanceLong+2)))

        # Left Middle
        if self.direction == NORTH:
            self.getValue(zip([r]*distanceLong, range(c-distanceLong-1, c-1))[::-1])
        elif self.direction == EAST:
            self.getValue(zip(range(r-distanceLong-1, r-1), [c]*distanceLong)[::-1])
        elif self.direction == WEST:
            self.getValue(zip(range(r+2, r+distanceLong+2), [c]*distanceLong))
        else:
            self.getValue(zip([r]*distanceLong, range(c+2, c+distanceLong+2)))

    def moveBot(self, movement):
        """Simulates the bot movement based on current location, direction and received action

        Args:
            movement (string): Next movement received (see Constants)
        """
        self.movement.append(movement)
        if self.direction == NORTH:
            if movement == RIGHT:
                self.direction = EAST
            elif movement == LEFT:
                self.direction = WEST
            else:
                self.center = self.center + [-1, 0]
                self.markArea(self.center, 1)
            self.setHead()
        elif self.direction == EAST:
            if movement == RIGHT:
                self.direction = SOUTH
            elif movement == LEFT:
                self.direction = NORTH
            else:
                self.center = self.center + [0, 1]
                self.markArea(self.center, 1)
            self.setHead()
        elif self.direction == SOUTH:
            if movement == RIGHT:
                self.direction = WEST
            elif movement == LEFT:
                self.direction = EAST
            else:
                self.center = self.center + [1, 0]
                self.markArea(self.center, 1)
            self.setHead()
        else:
            if movement == RIGHT:
                self.direction = NORTH
            elif movement == LEFT:
                self.direction = SOUTH
            else:
                self.center = self.center + [0, -1]
                self.markArea(self.center, 1)
            self.setHead()

    def descriptor_1(self):
        descriptor = np.zeros([20, 15]).astype(int)
        descriptor[self.exploredMap[::-1, :] != 0] = 1
        bits = '11'
        for row in descriptor:
            bits += ''.join(map(str, row.tolist()))
        bits += '11'
        hex_str = ['%X' % int(bits[i:i+4], 2) for i in range(0, len(bits)-3, 4)]
        return ''.join(hex_str)

    def descriptor_2(self):
        bits = ''
        for row in self.exploredMap[::-1, :]:
            for bit in row:
                if bit == 2:
                    bits += '1'
                elif bit != 0:
                    bits += '0'
        bits += '0'*(4 - len(bits) % 4)
        hex_str = ['%X' % int(bits[i:i+4], 2) for i in range(0, len(bits)-3, 4)]
        return ''.join(hex_str)

    def is_corner(self):
        """To check whether the robot is in a corner.

        Returns:
            bool: To represent whether there is a corner

        """
        r, c = self.center

        if self.direction == NORTH:
            fw = False
            fw = (r-2 == -1) or (r-2 != -1 and self.exploredMap[r-2][c-1] == 2
                                 and self.exploredMap[r-2][c+1] == 2)
            rw = (c+2 == MAX_COLS) or (c+2 != MAX_COLS
                                       and self.exploredMap[r-1][c+2] == 2
                                       and self.exploredMap[r+1][c+2] == 2)
            if fw and rw:
                return True
            else:
                return False
        elif self.direction == EAST:
            fw = (c+2 == MAX_COLS) or (c+2 != MAX_COLS
                                       and self.exploredMap[r-1][c+2] == 2
                                       and self.exploredMap[r+1][c+2] == 2)
            rw = (r+2 == MAX_ROWS) or (r+2 != MAX_ROWS
                                       and self.exploredMap[r+2][c-1] == 2
                                       and self.exploredMap[r+2][c+1] == 2)
            if fw and rw:
                return True
            else:
                return False
        elif self.direction == SOUTH:
            fw = (r+2 == MAX_ROWS) or (r+2 != MAX_ROWS
                                       and self.exploredMap[r+2][c-1] == 2
                                       and self.exploredMap[r+2][c+1] == 2)
            rw = (c-2 == -1) or (c-2 != -1 and self.exploredMap[r-1][c-2] == 2
                                 and self.exploredMap[r+1][c-2] == 2)
            if fw and rw:
                return True
            else:
                return False
        else:
            fw = (c-2 == -1) or (c-2 != -1 and self.exploredMap[r-1][c-2] == 2
                                 and self.exploredMap[r+1][c-2] == 2)
            rw = (r-2 == -1) or (r-2 != -1 and self.exploredMap[r-2][c-1] == 2
                                 and self.exploredMap[r-2][c+1] == 2)
            if fw and rw:
                return True
            else:
                return False

    def can_calibrate_front(self):
        """To calibrate the robot according to the front wall.

        Returns:
            flag (bool): Specify the direction to calibrate

        """
        r, c = self.center
        flag = [False, None]

        if self.direction == NORTH:
            for i in range(2, 3):
                if ((r - i) < 0):
                    flag = [True, 'F']
                    break
                elif ((r - i) >= 0 and (self.exploredMap[r-i][c-1] == 2
                      and self.exploredMap[r-i][c+1] == 2)):
                    flag = [True, 'F']
                    break
        elif self.direction == WEST:
            for i in range(2, 3):
                if ((c - i) < 0):
                    flag = [True, 'F']
                    break
                elif ((c - i) >= 0 and (self.exploredMap[r-1][c-i] == 2
                      and self.exploredMap[r+1][c-i] == 2)):
                    flag = [True, 'F']
                    break
        elif self.direction == EAST:
            for i in range(2, 3):
                if ((c + i) == MAX_COLS):
                    flag = [True, 'F']
                    break
                elif ((c + i) < MAX_COLS and (self.exploredMap[r-1][c+i] == 2
                      and self.exploredMap[r+1][c+i] == 2)):
                    flag = [True, 'F']
                    break
        else:
            for i in range(2, 3):
                if ((r + i) == MAX_ROWS):
                    flag = [True, 'F']
                    break
                elif ((r + i) < MAX_ROWS and (self.exploredMap[r+i][c-1] == 2
                      and self.exploredMap[r+i][c+1] == 2)):
                    flag = [True, 'F']
                    break
        return flag

    def can_calibrate_right(self):
        """To calibrate the robot according to the right wall.

        Returns:
            flag (bool): Specify the direction to calibrate

        """
        r, c = self.center
        flag = [False, None]

        if self.direction == NORTH:
            for i in range(2, 3):
                if ((c + i) == MAX_COLS):
                    flag = [True, 'R']
                    break
                elif ((c + i) < MAX_COLS and (self.exploredMap[r-1, c+i] == 2
                      and self.exploredMap[r+1, c+i] == 2)):
                    flag = [True, 'R']
                    break
        elif self.direction == WEST:
            for i in range(2, 3):
                if ((r - i) < 0):
                    flag = [True, 'R']
                    break
                elif ((r - i) >= 0 and (self.exploredMap[r-i, c-1] == 2 and
                      self.exploredMap[r-i, c+1] == 2)):
                    flag = [True, 'R']
                    break
        elif self.direction == EAST:
            for i in range(2, 3):
                if ((r + i) == MAX_ROWS):
                    flag = [True, 'R']
                    break
                elif ((r + i) < MAX_ROWS and (self.exploredMap[r+i, c-1] == 2
                      and self.exploredMap[r+i, c+1] == 2)):
                    flag = [True, 'R']
                    break
        else:
            for i in range(2, 3):
                if ((c - i) < 0):
                    flag = [True, 'R']
                    break
                elif ((c - i) >= 0 and (self.exploredMap[r-1, c-i] == 2 and
                      self.exploredMap[r+1, c-i] == 2)):
                    flag = [True, 'R']
                    break
        return flag
