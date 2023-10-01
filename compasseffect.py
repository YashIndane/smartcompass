import socket
import time
import stepperdriver


def getr(HOST:str, PORT:int) -> float:

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((HOST, PORT))
  BUFFER_SIZE = 1024
  data, add = sock.recvfrom(BUFFER_SIZE)
  data = str(data)[2:].split(',')

  X_ROT = float(data[0])
  sock.close()

  return X_ROT

def compass_effect_driver(HOST:str, PORT:int, MOTOR_PINS) -> None:

  old = 0.0
  delay = 0.05
  RESET_TUNING = 3.15

  stepperdriver.steppersetup(MOTOR_PINS)

  while True:

    a = getr(HOST, PORT)
    time.sleep(delay)
    b = getr(HOST, PORT)

    if (0<=a<45 and 270<=b<=360):
      an = int(round(RESET_TUNING*(b-a-360)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)

    elif (0<=b<=45 and 270<=a<=360):
      an = int(round(RESET_TUNING*(b-a+360)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)

    else:
      an = int(round(RESET_TUNING*(b-a)))
      stepperdriver.driver_stepper(-an, MOTOR_PINS)
