#!/usr/bin/python3

#sudo python3 stepper-test.py

import RPi.GPIO as GPIO
import time

in1 = 17
in2 = 18
in3 = 27
in4 = 22

#rotation angle in degress
angle = 164

step_sleep = 0.001

step_count = int(round((angle/360)*4096))

#false for anticlock and True for clock
direction = True

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

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)

motor_pins = [in1, in2, in3, in4]
motor_step_counter = 0;

def cleanup():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    GPIO.cleanup()

try:
    i=0
    for i in range(step_count):
        for pin in range(0, len(motor_pins)):
            GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
        if direction==True:
            motor_step_counter = (motor_step_counter-1) % 8
        elif direction==False:
            motor_step_counter = (motor_step_counter+1) % 8
        else:
            print("give direction as True or False")
            cleanup()
            exit(1)

        time.sleep(step_sleep)

except KeyboardInterrupt:
    cleanup()
    exit(1)

cleanup()
exit(0)
