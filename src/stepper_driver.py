#!/usr/bin/python3

# Stepper motor driver module.

import time
import RPi.GPIO as GPIO

from typing import List


class Stepper:
    def __init__(self, *, motor_pins: List[int]) -> None:
        self.motor_pins = motor_pins
  
    def steppersetup(self) -> None:
        """Sets the RPI pins for driving the stepper

        :return: None
        """
        GPIO.setmode(GPIO.BCM)
    
        for pin in self.motor_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)


    def cleanup(self) -> None:
        for m_pins in self.motor_pins:
            GPIO.output(m_pins, GPIO.LOW)
            # GPIO.cleanup()


    def driver_stepper(self, *, angle: int) -> None:
        """Main stepper driving code

        :param angle: Angle to drive (type int)
        :return: None
        """
  
        step_count = int(
            round((abs(angle) / 360) * 4096)
        )

        motor_step_counter = 0

        # Lower the STEP_SLEEP considering mechanical constraints of the motor
        STEP_SLEEP = .002
        direction = angle > 0

        step_sequence = [
            [1,0,0,1],
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1]
        ]

        try:
            i=0
            for i in range(step_count):
                for pin in range(0, len(self.motor_pins)):
                    GPIO.output(
                        self.motor_pins[pin], step_sequence[motor_step_counter][pin]
                    )
                if direction == True:
                    motor_step_counter = (motor_step_counter - 1) % 8
                elif direction == False:
                    motor_step_counter = (motor_step_counter + 1) % 8
                else:
                    print("Give direction as True or False")
                    self.cleanup(self.motor_pins)
                    exit(1)

                time.sleep(STEP_SLEEP)

        except KeyboardInterrupt:
            self.cleanup()
            exit(1)

        self.cleanup()
        #exit(0)
