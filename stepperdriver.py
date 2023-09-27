#!/usr/bin/python3

#sudo python3 stepper-test.py

import RPi.GPIO as GPIO
import time

def steppersetup(motor_pins:list) -> None:

  GPIO.setmode(GPIO.BCM)

  for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

  for pin in motor_pins:
    GPIO.output(pin, GPIO.LOW)


def cleanup(motor_pins:list):

  for m_pins in motor_pins:
    GPIO.output(m_pins, GPIO.LOW)
  #GPIO.cleanup()


def driver_stepper(angle:int, motor_pins:list) -> None:
  
  step_count = int(round((abs(angle)/360)*4096))
  motor_step_counter = 0
  STEP_SLEEP = 0.002
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
      for pin in range(0, len(motor_pins)):
        GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
      if direction == True:
        motor_step_counter = (motor_step_counter-1) % 8
      elif direction == False:
        motor_step_counter = (motor_step_counter+1) % 8
      else:
        print("give direction as True or False")
        cleanup(motor_pins)
        exit(1)

      time.sleep(STEP_SLEEP)

  except KeyboardInterrupt:
    cleanup(motor_pins)
    exit(1)

  cleanup(motor_pins)
  #exit(0)
