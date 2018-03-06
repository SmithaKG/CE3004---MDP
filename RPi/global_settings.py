import logging
import numpy as np


def init():

    global RPI_SENDER
    global RPI_ALGORITHM_SIGNAL
    global RPI_ANDROID_SIGNAL
    global RPI_ARDUINO_SIGNAL

    global ALGORITHM_SENDER
    global ALGORITHM_SIGNAL

    global ANDROID_SENDER
    global ANDROID_SIGNAL

    global ARDUINO_SENDER
    global ARDUINO_SIGNAL

    RPI_SENDER = 'rpi_sender'
    RPI_ALGORITHM_SIGNAL = 'rpi_algorithm_signal'
    RPI_ANDROID_SIGNAL = 'rpi_android_signal'
    RPI_ARDUINO_SIGNAL = 'rpi_arduino_signal'

    ALGORITHM_SENDER = 'algorithm_sender'
    ALGORITHM_SIGNAL = 'algorithm_signal'

    ANDROID_SENDER = 'android_sender'
    ANDROID_SIGNAL = 'android_signal'

    ARDUINO_SENDER = 'arduino_sender'
    ARDUINO_SIGNAL = 'arduino_signal'

    global MAZEMAP
    _row = 20
    _col = 15
    MAZEMAP = np.zeros([_row, _col], dtype=int)

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.INFO)


def print_mazemap(mmap):
    for mazerow in mmap:
        for grid in mazerow:
            if grid is None:
                print "?",
            else:
                print grid,
        print ""


def get_obstacle_mazemap(mmap):
    return np.where(mmap > 1, 1, 0)


def get_explore_status_mazemap(mmap):
    return np.where(mmap > 0, 1, 0)


def get_mdf_bitstring(mmap, format=0):
    bitstring = '11' + ''.join(str(grid) for mazerow in mmap for grid in mazerow) + '11'
    if format == 0:     # binary
        return bin(int(bitstring, 2))[2:]
    if format == 1:     # hexadecimal
        return hex(int(bitstring, 2))[2:]
    assert False, "unhandled format"


def aggregate_instruction(instruction):
    if len(instruction) == 0:
        return []

    instruction_list = [ch + '1' for ch in instruction]
    updatedInstruction = [instruction_list[0]]
    for ch in instruction_list[1:]:
        if (ch[0] != updatedInstruction[-1][0]):
            updatedInstruction.append(ch)
        else:
            # updatedInstruction[-1] = updatedInstruction[-1][0] + str(int(updatedInstruction[-1][1:]) + 1)
            updatedInstruction[-1] = updatedInstruction[-1][0] + chr(ord(updatedInstruction[-1][1:]) + 1)
    return updatedInstruction
