#!/usr/bin/python3

# The compass effect module. It locks the needle no matter whichever direction you turn.


import socket
import time
import RPi.GPIO as GPIO

from typing import List
from src.stepper_driver import Stepper


def getr(*, HOST: str, PORT: int) -> float:
    """Read the current device heading

    :param HOST: HOST IP Adderss (type str)
    :param PORT: UDP PORT (type int)
    :return: Heading angle (type float)
    """

    BUFFER_SIZE = 1024
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    data, add = sock.recvfrom(BUFFER_SIZE)
    data = str(data)[2:].split(',')
    X_ROT = float(data[0])
    sock.close()

    return X_ROT


def compass_effect_driver(
    *,
    HOST: str,
    PORT: int,
    MOTOR_PINS: List[int],
    keypad_lines: List[int],
    keypad_columns: List[int],
) -> int:
    """Main compass effect code

    :param HOST: HOST IP (type str)
    :param PORT: UDP PORT (type int)
    :param MOTOR_PINS: Motor GPIO pins (type List[int])
    :param keypad_line: Keypad lines (type List[int])
    :param keypad_columns: Keypad columns (type List[int])
    :return: Corrected reset angle (type int)
    """

    old = 0.0
    delay = .05

    # Used to tune the differnce in angle readings
    RESET_TUNING = 3.15
    reset_angle_correction = 0
    
    stp = Stepper(motor_pins=MOTOR_PINS)
    stp.steppersetup()

    while True:
        a: float = getr(HOST=HOST, PORT=PORT)
        time.sleep(delay)
        b: float = getr(HOST=HOST, PORT=PORT)

        if (0<=a<45 and 270<=b<=360):
            an = int(round(RESET_TUNING * (b - a - 360)))
            stp.driver_stepper(angle=-an)
            reset_angle_correction += an

        elif (0<=b<=45 and 270<=a<=360):
            an = int(round(RESET_TUNING * (b - a + 360)))
            stp.driver_stepper(angle=-an)
            reset_angle_correction += an

        else:
            an = int(round(RESET_TUNING * (b - a)))
            stp.driver_stepper(angle=-an)
            reset_angle_correction += an

        GPIO.output(keypad_lines[3], GPIO.HIGH)
        reset_check: bool = GPIO.input(keypad_columns[3]) == 1

        if reset_check:
            print("exited compass effect")
            GPIO.output(keypad_lines[3], GPIO.LOW)
            return reset_angle_correction
