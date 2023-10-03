import socket
import time
import stepperdriver
import RPi.GPIO as GPIO


def getr(HOST:str, PORT:int) -> float:

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((HOST, PORT))
  BUFFER_SIZE = 1024
  data, add = sock.recvfrom(BUFFER_SIZE)
  data = str(data)[2:].split(',')

  X_ROT = float(data[0])
  sock.close()

  return X_ROT


def compass_effect_driver(HOST:str, PORT:int, MOTOR_PINS, keypad_line, keypad_columns) -> int:

  old = 0.0
  delay = 0.05
  RESET_TUNING = 3.15
  reset_angle_correction = 0

  stepperdriver.steppersetup(MOTOR_PINS)

  while True:

    a = getr(HOST, PORT)
    time.sleep(delay)
    b = getr(HOST, PORT)

    if (0<=a<45 and 270<=b<=360):
      an = int(round(RESET_TUNING*(b-a-360)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)
      reset_angle_correction += an

    elif (0<=b<=45 and 270<=a<=360):
      an = int(round(RESET_TUNING*(b-a+360)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)
      reset_angle_correction += an

    else:
      an = int(round(RESET_TUNING*(b-a)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)
      reset_angle_correction += an

    GPIO.output(keypad_line[3], GPIO.HIGH)
    reset_check = GPIO.input(keypad_columns[3]) == 1

    if reset_check:
      print("yeh")
      GPIO.output(keypad_line[3], GPIO.LOW)
      return reset_angle_correction 
