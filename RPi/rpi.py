import logging
import time
import threading
import sys

from pydispatch import dispatcher

import global_settings as gs


class RPI(threading.Thread):
    def __init__(self):

        super(RPI, self).__init__()
        self.running = False

        dispatcher.connect(self.command_rpi, signal=gs.ANDROID_SIGNAL, sender=gs.ANDROID_SENDER)
        dispatcher.connect(self.command_arduino, signal=gs.ALGORITHM_SIGNAL, sender=gs.ALGORITHM_SENDER)
        dispatcher.connect(self.command_algorithm, signal=gs.ARDUINO_SIGNAL, sender=gs.ARDUINO_SENDER)

        logging.info("rpi +initialized")

    def command_rpi(self, message):
        logging.info("rpi received message from android and write message: " + str(message))

    def command_arduino(self, message):
        """
        Message received from algorithm to be processed and passed to arduino
        """
        # if fatest path
        if len(message) == 1:
            formatted_instruction = 'C' + ''.join(instruction)
            # aggregate the movement
        # if exploration
        if len(message) > 1:

            instruction = message[0]

            completed = message[1]

            robot_row = message[2][0]
            robot_col = message[2][1]
            robot_dir = message[3]

            if not completed:
                formatted_instruction = 'S' + ''.join(instruction)
                robot_moving_stop_string_update = '1L'   # robot no longer moving after instruction
            else:
                # exploration completed, arduino do not need to sense environment
                # after moving robot
                formatted_instruction = 'C' + ''.join(instruction)
                robot_moving_stop_string_update = '0L'   # robot still going moving after instruction

            explore_mdf_string_update = gs.get_mdf_bitstring(gs.get_explore_status_mazemap(gs.MAZEMAP), 1)
            obstacle_mdf_string_update = gs.get_mdf_bitstring(gs.get_obstacle_mazemap(gs.MAZEMAP), 1)
            robot_location_string_update = str(robot_row) + 'L' + str(robot_col) + 'L'
            robot_direction_string_update = str(robot_dir) + 'L'

            update_string = explore_mdf_string_update + obstacle_mdf_string_update + robot_location_string_update + robot_direction_string_update + robot_moving_stop_string_update
            self.feedback_android(update_string)

        dispatcher.send(message=formatted_instruction, signal=gs.RPI_ARDUINO_SIGNAL, sender=gs.RPI_SENDER)
        logging.info("rpi received message from algorithm and write message to arduino: " + str(formatted_instruction))

    def command_algorithm(self, message):
        """
        - Message received from arduino to be processed and passed to algorithm
        - Updates from Arduino to be processed and passed to Android
        """
        dispatcher.send(message=message, signal=gs.RPI_ALGORITHM_SIGNAL, sender=gs.RPI_SENDER)
        logging.info("rpi received message from arduino and send message to algorithm: " + str(message))

    def feedback_android(self, message):
        dispatcher.send(message=message, signal=gs.RPI_ANDROID_SIGNAL, sender=gs.RPI_SENDER)
        logging.info("rpi send feedback message to android: " + str(message))

    def start(self):
        self.running = True
        super(RPI, self).start()

    def run(self):
        self.idle()

    def stop(self):
        self.running = False

    def idle(self):
        while(self.running):
            time.sleep(1)
